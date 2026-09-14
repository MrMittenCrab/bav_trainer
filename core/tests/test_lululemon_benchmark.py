"""Step 9M.2 — Lululemon real-company benchmark baseline acceptance."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from core.data.standardized_io import standardized_from_payload
from core.ingestion.filing_json import load_extracted_filing
from core.ingestion.filing_validator import validate_extracted_filing
from core.model.classification import (
    UnclassifiedBalanceSheetLineError,
    classify_balance_sheet_line,
    is_balance_sheet_subtotal,
)
from core.model.fixed_asset import fixed_asset_applicable, fixed_asset_availability
from core.model.line_resolver import resolve_line
from core.trainer.workbook import build_training_workbook

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark" / "lululemon"
EXTRACTED = BENCH / "extracted"
SOURCE = BENCH / "source"
RECONCILED = BENCH / "reconciled"
STD_JSON = RECONCILED / "standardized.json"
PROV_JSON = RECONCILED / "provenance.json"
CONFLICTS_JSON = RECONCILED / "conflicts.json"

SOURCE_PDFS = {
    2022: (
        "LULU_FY2022_Annual_Report.pdf",
        "b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e",
        4913067,
    ),
    2023: (
        "LULU_FY2023_Annual_Report.pdf",
        "cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1",
        5848446,
    ),
    2024: (
        "LULU_FY2024_Annual_Report.pdf",
        "9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec",
        5953217,
    ),
    2025: (
        "LULU_FY2025_Annual_Report.pdf",
        "82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc",
        6590658,
    ),
}

EXPECTED_PERIODS = [
    date(2023, 1, 29),
    date(2024, 1, 28),
    date(2025, 2, 2),
    date(2026, 2, 1),
]

REVENUE_ANCHORS = {
    date(2023, 1, 29): 8110518.0,
    date(2024, 1, 28): 9619278.0,
    date(2025, 2, 2): 10588126.0,
    date(2026, 2, 1): 11102600.0,
}

DILUTED_WAS_ANCHORS = {
    date(2023, 1, 29): 128017.0,
    date(2024, 1, 28): 127060.0,
    date(2025, 2, 2): 123935.0,
    date(2026, 2, 1): 119068.0,
}

BUILD_BLOCKER_LABELS = {
    "Common stock",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_four_filings_validate_and_remain_source_bound():
    files = sorted(EXTRACTED.glob("LULU_FY*.json"))
    assert {int(p.stem.replace("LULU_FY", "")) for p in files} == {2022, 2023, 2024, 2025}

    for fiscal_year, (pdf_name, digest, nbytes) in SOURCE_PDFS.items():
        pdf = SOURCE / pdf_name
        assert pdf.is_file()
        data = pdf.read_bytes()
        assert len(data) == nbytes
        assert hashlib.sha256(data).hexdigest() == digest

        extracted = EXTRACTED / f"LULU_FY{fiscal_year}.json"
        filing = load_extracted_filing(extracted)
        assert filing.schema_version == "1.0"
        assert filing.filing.fiscal_year == fiscal_year
        assert filing.filing.source_file == pdf_name
        assert filing.income_statement
        assert filing.balance_sheet
        assert filing.cash_flow

        report = validate_extracted_filing(filing, source_root=SOURCE)
        assert report.ok
        assert report.computed_source_sha256 == digest
        assert report.warnings == ()


def _reconcile_cmd(out: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "core",
        "reconcile",
        str(EXTRACTED),
        "--source-root",
        str(SOURCE),
        "-o",
        str(out),
    ]


def _subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return env


ARTIFACT_NAMES = ("standardized.json", "provenance.json", "conflicts.json")


def _read_committed_artifacts() -> dict[str, bytes]:
    return {name: (RECONCILED / name).read_bytes() for name in ARTIFACT_NAMES}


def _assert_artifact_sets_match(
    generated: Path,
    expected_bytes: dict[str, bytes],
) -> None:
    """Compare generated artifacts to expected bytes; never write expected paths."""
    mismatches: list[str] = []
    for name in ARTIFACT_NAMES:
        actual = (generated / name).read_bytes()
        if actual != expected_bytes[name]:
            mismatches.append(name)
    if mismatches:
        raise AssertionError(
            "reconciliation artifact mismatch: " + ", ".join(mismatches)
        )


def _run_reconcile_pass(out: Path) -> None:
    completed = subprocess.run(
        _reconcile_cmd(out),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert "overlap_conflicts=" in completed.stdout


def _assert_inter_run_artifacts_match(out1: Path, out2: Path) -> None:
    for name in ARTIFACT_NAMES:
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()


def _assert_committed_artifacts_unchanged(committed_before: dict[str, bytes]) -> None:
    committed_after = _read_committed_artifacts()
    mutated = [
        name
        for name in ARTIFACT_NAMES
        if committed_after[name] != committed_before[name]
    ]
    if mutated:
        raise AssertionError(
            "committed reconciliation artifacts mutated: " + ", ".join(mutated)
        )


def _guarded_deterministic_reconcile(
    tmp_path: Path,
    *,
    committed_before: dict[str, bytes] | None = None,
    run_pass=_run_reconcile_pass,
    assert_inter_run=_assert_inter_run_artifacts_match,
    assert_baseline=_assert_artifact_sets_match,
    read_committed=_read_committed_artifacts,
) -> None:
    """Run both reconcile passes under try; always re-verify committed bytes in finally."""
    if committed_before is None:
        committed_before = read_committed()
    out1 = tmp_path / "r1"
    out2 = tmp_path / "r2"
    error: BaseException | None = None
    try:
        run_pass(out1)
        run_pass(out2)
        assert_inter_run(out1, out2)
        assert_baseline(out1, committed_before)
        assert_baseline(out2, committed_before)
    except BaseException as exc:
        error = exc
    finally:
        try:
            after = read_committed()
            mutated = [
                name
                for name in ARTIFACT_NAMES
                if after[name] != committed_before[name]
            ]
            if mutated:
                raise AssertionError(
                    "committed reconciliation artifacts mutated: "
                    + ", ".join(mutated)
                )
        except AssertionError:
            raise
        else:
            if error is not None:
                raise error


def test_generic_reconcile_is_deterministic(tmp_path: Path):
    committed_before = _read_committed_artifacts()
    _guarded_deterministic_reconcile(tmp_path, committed_before=committed_before)


@pytest.mark.parametrize("fail_pass", [1, 2])
def test_reconcile_immutability_verified_after_subprocess_failure(
    tmp_path: Path, fail_pass: int
):
    """Subprocess failure still triggers final committed-byte verification."""
    committed_before = _read_committed_artifacts()
    calls = {"n": 0}
    verified = {"ok": False}

    def boom_pass(out: Path) -> None:
        calls["n"] += 1
        if calls["n"] == fail_pass:
            raise subprocess.CalledProcessError(1, _reconcile_cmd(out))
        _run_reconcile_pass(out)

    def tracking_read() -> dict[str, bytes]:
        verified["ok"] = True
        return _read_committed_artifacts()

    with pytest.raises(subprocess.CalledProcessError):
        _guarded_deterministic_reconcile(
            tmp_path,
            committed_before=committed_before,
            run_pass=boom_pass,
            read_committed=tracking_read,
        )
    assert verified["ok"]
    _assert_committed_artifacts_unchanged(committed_before)


@pytest.mark.parametrize("fail_at", ["inter_run", "baseline"])
def test_reconcile_immutability_verified_after_comparison_failure(
    tmp_path: Path, fail_at: str
):
    """Comparison failure still triggers final committed-byte verification."""
    committed_before = _read_committed_artifacts()
    verified = {"ok": False}

    def boom_inter(out1: Path, out2: Path) -> None:
        raise AssertionError("injected inter-run mismatch")

    def boom_baseline(generated: Path, expected_bytes: dict[str, bytes]) -> None:
        raise AssertionError("injected baseline mismatch")

    def tracking_read() -> dict[str, bytes]:
        verified["ok"] = True
        return _read_committed_artifacts()

    kwargs: dict = {
        "committed_before": committed_before,
        "read_committed": tracking_read,
    }
    if fail_at == "inter_run":
        kwargs["assert_inter_run"] = boom_inter
        match = "injected inter-run mismatch"
    else:
        kwargs["assert_baseline"] = boom_baseline
        match = "injected baseline mismatch"

    with pytest.raises(AssertionError, match=match):
        _guarded_deterministic_reconcile(tmp_path, **kwargs)
    assert verified["ok"]
    _assert_committed_artifacts_unchanged(committed_before)


@pytest.mark.parametrize("mutated_name", ARTIFACT_NAMES)
@pytest.mark.parametrize("fail_at", ["pass1", "inter_run", "baseline"])
def test_reconcile_immutability_guard_detects_temp_mutation(
    tmp_path: Path, mutated_name: str, fail_at: str
):
    """Temp artifact mutation before injected failure is detected by the finally guard."""
    expected_dir = tmp_path / "expected"
    expected_dir.mkdir()
    for name in ARTIFACT_NAMES:
        (expected_dir / name).write_bytes((RECONCILED / name).read_bytes())

    def read_temp() -> dict[str, bytes]:
        return {name: (expected_dir / name).read_bytes() for name in ARTIFACT_NAMES}

    committed_before = read_temp()
    mutated_path = expected_dir / mutated_name
    altered = mutated_path.read_bytes() + b"\n#mutated\n"
    finally_saw_mutation = {"ok": False}

    def mutate_then_fail_pass(out: Path) -> None:
        mutated_path.write_bytes(altered)
        raise subprocess.CalledProcessError(1, ["fake"])

    def mutate_then_fail_inter(out1: Path, out2: Path) -> None:
        mutated_path.write_bytes(altered)
        raise AssertionError("injected inter-run mismatch")

    def mutate_then_fail_baseline(
        generated: Path, expected_bytes: dict[str, bytes]
    ) -> None:
        mutated_path.write_bytes(altered)
        raise AssertionError("injected baseline mismatch")

    def read_temp_tracking() -> dict[str, bytes]:
        current = read_temp()
        if current[mutated_name] != committed_before[mutated_name]:
            finally_saw_mutation["ok"] = True
        return current

    kwargs: dict = {
        "committed_before": committed_before,
        "read_committed": read_temp_tracking,
    }
    if fail_at == "pass1":
        kwargs["run_pass"] = mutate_then_fail_pass
    elif fail_at == "inter_run":
        kwargs["assert_inter_run"] = mutate_then_fail_inter
    else:
        kwargs["assert_baseline"] = mutate_then_fail_baseline

    with pytest.raises(AssertionError, match=mutated_name):
        _guarded_deterministic_reconcile(tmp_path, **kwargs)

    assert finally_saw_mutation["ok"]
    assert mutated_path.read_bytes() == altered
    for name in ARTIFACT_NAMES:
        if name == mutated_name:
            continue
        assert (expected_dir / name).read_bytes() == (RECONCILED / name).read_bytes()


@pytest.mark.parametrize("drifted_name", ARTIFACT_NAMES)
def test_reconcile_drift_is_detected_without_rewriting_expected(
    tmp_path: Path, drifted_name: str
):
    """Altering a temp expected copy must fail comparison and leave that copy intact."""
    expected_dir = tmp_path / "expected"
    expected_dir.mkdir()
    for name in ARTIFACT_NAMES:
        (expected_dir / name).write_bytes((RECONCILED / name).read_bytes())

    drifted_path = expected_dir / drifted_name
    original_expected = drifted_path.read_bytes()
    drifted_path.write_bytes(original_expected + b"\n#drift\n")
    altered_expected = drifted_path.read_bytes()
    assert altered_expected != original_expected

    expected_bytes = {name: (expected_dir / name).read_bytes() for name in ARTIFACT_NAMES}

    out = tmp_path / "generated"
    completed = subprocess.run(
        _reconcile_cmd(out),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert "overlap_conflicts=" in completed.stdout

    with pytest.raises(AssertionError, match=drifted_name):
        _assert_artifact_sets_match(out, expected_bytes)

    assert drifted_path.read_bytes() == altered_expected
    for name in ARTIFACT_NAMES:
        if name == drifted_name:
            continue
        assert (expected_dir / name).read_bytes() == (RECONCILED / name).read_bytes()


def test_reconciled_axis_anchors_and_conflicts():
    payload = _load_json(STD_JSON)
    provenance = _load_json(PROV_JSON)
    conflicts = _load_json(CONFLICTS_JSON)
    fin = standardized_from_payload(payload)

    assert fin.ticker == "LULU"
    assert fin.company_name == "lululemon athletica inc."
    assert fin.currency == "USD"
    assert fin.units == "USD in Thousands"
    assert fin.jurisdiction == "US"
    assert [p.end_date for p in fin.periods] == EXPECTED_PERIODS

    # Four FY2022–FY2025 filing year-ends are on the axis. Earlier comparative
    # IS dates present in extracted filings are not promoted onto the canonical axis.
    assert len(fin.periods) == 4

    revenue = next(item for item in fin.income_statement if item.concept == "revenue")
    assert {p: revenue.values[p] for p in EXPECTED_PERIODS} == REVENUE_ANCHORS

    assert fin.historical_shares is not None
    assert fin.historical_shares.scale_basis == "financial_statement_units"
    assert fin.historical_shares.basis == "reported"
    assert fin.historical_shares.diluted_weighted_average == DILUTED_WAS_ANCHORS

    assert conflicts["overlap_conflict_count"] == 3
    assert conflicts["supplemental_conflict_count"] == 0
    assert len(conflicts["conflicts"]) == 3

    source_files = provenance["source_files"]
    assert len(source_files) == 4
    by_year = {entry["filing_year"]: entry for entry in source_files}
    assert set(by_year) == {2022, 2023, 2024, 2025}
    for year, (pdf_name, digest, _) in SOURCE_PDFS.items():
        assert by_year[year]["source_file"] == pdf_name
        assert by_year[year]["source_sha256"] == digest


def test_gift_card_liability_classifies_across_all_periods():
    """G1: unchanged Lululemon gift-card row is operating WC liability in every period."""
    fin = standardized_from_payload(_load_json(STD_JSON))
    item = next(
        row
        for row in fin.balance_sheet
        if row.concept == "unredeemed_gift_card_liability"
        and row.label == "Unredeemed gift card liability"
    )
    assert set(item.values) >= set(EXPECTED_PERIODS)
    decision = classify_balance_sheet_line(item)
    assert decision.category == "Operating Working Capital Liability"
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.overridden is False
    for period in EXPECTED_PERIODS:
        assert item.values[period] is not None


def test_ppe_classifies_resolves_and_enables_fixed_asset():
    """G2: PPE row classifies/resolves with all four periods; fixed-asset unlocks."""
    fin = standardized_from_payload(_load_json(STD_JSON))
    original_index, item = next(
        (idx, row)
        for idx, row in enumerate(fin.balance_sheet)
        if row.concept == "property_plant_and_equipment"
        and row.label == "Property and equipment, net"
    )
    assert set(item.values) >= set(EXPECTED_PERIODS)
    for period in EXPECTED_PERIODS:
        assert item.values[period] is not None

    decision = classify_balance_sheet_line(item)
    assert decision.category == "Operating Long-Term Asset"
    assert decision.ambiguous is False
    assert decision.judgment_code is None
    assert decision.overridden is False

    resolved = resolve_line(
        fin.balance_sheet, "property_plant_equipment", required=True
    )
    assert resolved.index == original_index
    assert resolved.item is item
    assert resolved.item.concept == "property_plant_and_equipment"

    avail = fixed_asset_availability(fin)
    assert avail.ppe is True
    assert avail.depreciation_amortization is True
    assert fixed_asset_applicable(fin) is True


def test_build_blocker_is_unclassified_balance_sheet_lines(tmp_path: Path):
    """After G2, build remains blocked on Common stock only.

    First raise is Common stock; G1 gift-card and G2 PPE remain classified.
    """
    fin = standardized_from_payload(_load_json(STD_JSON))

    unclassified = set()
    for item in fin.balance_sheet:
        if is_balance_sheet_subtotal(item):
            continue
        try:
            classify_balance_sheet_line(item)
        except UnclassifiedBalanceSheetLineError:
            unclassified.add(item.label)
    assert unclassified == BUILD_BLOCKER_LABELS

    gift = next(
        row
        for row in fin.balance_sheet
        if row.label == "Unredeemed gift card liability"
        and row.concept == "unredeemed_gift_card_liability"
    )
    assert (
        classify_balance_sheet_line(gift).category
        == "Operating Working Capital Liability"
    )

    ppe = next(
        row
        for row in fin.balance_sheet
        if row.label == "Property and equipment, net"
        and row.concept == "property_plant_and_equipment"
    )
    assert (
        classify_balance_sheet_line(ppe).category == "Operating Long-Term Asset"
    )

    out = tmp_path / "Lululemon"
    with pytest.raises(
        UnclassifiedBalanceSheetLineError, match="Common stock"
    ):
        build_training_workbook(fin, out)

def test_no_lulu_specific_production_branch():
    """Production engine must stay generic — no ticker/issuer hard-codes."""
    core_root = ROOT / "core"
    offenders: list[str] = []
    for path in core_root.rglob("*.py"):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for token in ("LULU", "lululemon", "Lululemon"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")
    assert offenders == []


def test_committed_reconciled_hashes_are_stable():
    """Lock measured baseline artifact digests for Step 9M.2."""
    assert _sha256(STD_JSON) == (
        "ba1ba06857198361706c368df490e4b874f8f03e7b45eaeb0af59eaa02aa4f45"
    )
    assert _sha256(CONFLICTS_JSON) == (
        "d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0"
    )
    # provenance is large; lock size + digest together
    assert PROV_JSON.stat().st_size == 698793
    assert _sha256(PROV_JSON) == (
        "2d4d770e7fede9d30a576ba82c031157895fee5224a3094f034fc466e546d269"
    )
