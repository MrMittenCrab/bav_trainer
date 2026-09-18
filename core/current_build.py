"""Project company resolution and verified, atomic current-snapshot publication.

Company metadata selects evidence locations, never accounting behavior. All
source additions still pass the existing source binding and admission pipeline.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from datetime import date
import json
import os
import re
from pathlib import Path
import shutil
import sys
import tempfile

from .data.standardized_io import standardized_to_payload
from .ingestion.filing_cli import load_and_validate_extracted_dir
from .ingestion.filing_reconciler import reconcile_filings
from .ingestion.filing_standardizer import (
    standardize_reconciled, reconciliation_provenance_payload,
    reconciliation_conflicts_payload, reconciliation_management_admission_payload,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / 'build/output'
# These are project routing/admission settings, not analytical special cases.
PROJECTS = tuple(
    (item['name'], item['slug'], tuple(item['aliases']),
     tuple(item['admit_periods']), item['supplemental_facts'])
    for item in json.loads(Path(__file__).with_name('project_companies.json').read_text())
)


@dataclass(frozen=True)
class Company:
    name: str
    slug: str
    aliases: tuple[str, ...]
    admit_periods: tuple[str, ...]
    supplemental_facts: str | None
    benchmark: Path
    output: Path

    @property
    def trainer(self):
        return self.output / f'{self.name}_Trainer.xlsx'

    @property
    def answer(self):
        return self.output / f'{self.name}_Answer_Key.xlsx'


def resolve_company(query: str) -> Company:
    key = query.strip().casefold()
    matches = [p for p in PROJECTS if key in {s.casefold() for s in (p[0], p[1], *p[2])}]
    if len(matches) != 1:
        label = 'Ambiguous' if matches else 'Unknown'
        candidates = ', '.join(p[0] for p in (matches or PROJECTS))
        raise ValueError(f'{label} company {query!r}; candidates: {candidates}')
    name, slug, aliases, periods, facts = matches[0]
    return Company(name, slug, aliases, periods, facts, ROOT / 'benchmark' / slug, OUTPUT_ROOT / name)


def current_workbook(query: str, *, answer: bool = False) -> Path:
    company = resolve_company(query)
    path = company.answer if answer else company.trainer
    if not path.is_file():
        raise ValueError(f'No current build for {company.name}; run python -m bav build {company.name}')
    return path


def _write_json(path: Path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def prepare_company_input(company: Company, staged: Path):
    """Reconcile fresh source-bound inputs; never fall back to stale reconciliation."""
    supporting = staged / 'supporting'
    supporting.mkdir(parents=True, exist_ok=True)
    extracted = company.benchmark / 'extracted'
    if company.supplemental_facts:
        # Existing vetted note-fact handoff. Keep ALL filings/management documents;
        # the helper itself only writes the annual filings named by the handoff.
        from .ingestion.note_handoff import augment_extracted_filings
        copied = supporting / 'extracted'
        shutil.copytree(extracted, copied)
        facts = ROOT / company.supplemental_facts
        augment_extracted_filings(extracted, copied, facts)
        shutil.copy2(facts, supporting / 'supplemental_facts.json')
        extracted = copied
    validated = load_and_validate_extracted_dir(extracted, source_root=company.benchmark / 'source')
    errors = [f'{filing.filing.source_file}: {issue.code}: {issue.message}'
              for filing, report in validated for issue in report.errors]
    errors += [f'{bound.document.extraction_document}: {issue.code}: {issue.message}'
               for bound in validated.management_documents for issue in bound.issues]
    if errors:
        raise ValueError('Source validation failed: ' + '; '.join(errors))
    reconciled = reconcile_filings(validated, admit_periods=tuple(date.fromisoformat(p) for p in company.admit_periods) or None)
    fin = standardize_reconciled(reconciled)
    _write_json(supporting / 'standardized.json', standardized_to_payload(fin))
    _write_json(supporting / 'provenance.json', reconciliation_provenance_payload(reconciled))
    _write_json(supporting / 'conflicts.json', reconciliation_conflicts_payload(reconciled))
    admission = reconciliation_management_admission_payload(reconciled)
    if admission is not None:
        _write_json(supporting / 'management_kpi_admission.json', admission)
    return fin


def verify_staged(fin, trainer: Path, answer: Path, assumptions=None):
    """Verify model identities, both learning surfaces, sidecars, and blank Check."""
    from openpyxl import load_workbook
    from .engine.reference_model import ReferenceModelBuilder
    from .engine.build_contract import verify_complete_build
    from .engine.component_catalog import is_operating_kpi_source_identity
    from .engine.semantic_map import SemanticMap
    from .trainer.semantic_io import load_semantic_map
    from .trainer.checker import check_workbook
    for path in (answer.with_suffix('.component_map.json'), answer.with_suffix('.assumptions.json'), answer.parent / 'rowmap.json'):
        if not path.is_file():
            raise ValueError(f'Missing required sidecar: {path.name}')
        json.loads(path.read_text())
    smap = load_semantic_map(answer)
    builder = ReferenceModelBuilder(fin, assumptions, current_snapshot=True)
    verify_complete_build(builder.expected_specs, smap)
    embedded = SemanticMap.from_workbook(answer)
    if [c.to_dict() for c in embedded.all_ordered()] != [c.to_dict() for c in smap.all_ordered()]:
        raise ValueError('Embedded and sidecar semantic maps differ')
    for path in (trainer, answer):
        wb = load_workbook(path)
        try:
            if 'Build Status' not in wb:
                raise ValueError('Missing Build Status')
            for comp in smap.all_ordered():
                cell = wb[comp.tab][comp.cell]
                if is_operating_kpi_source_identity(comp):
                    if cell.value is None:
                        raise ValueError('Missing supplied KPI fact')
                elif path == trainer:
                    if cell.value is not None or cell.comment is not None or cell.fill.fgColor.rgb not in ('00FFFF00', 'FFFFFF00'):
                        raise ValueError('Trainer practice invariant failed')
                elif cell.value != comp.formula or cell.comment is None:
                    raise ValueError('Answer Key formula/Note invariant failed')
            if path == answer and any(c.fill.fgColor.type == 'rgb' and c.fill.fgColor.rgb in ('FFFFFF00', '00FFFF00') for ws in wb for row in ws for c in row):
                raise ValueError('Answer Key has yellow fill')
        finally:
            wb.close()
    result = check_workbook(trainer)
    if result.correct or result.incorrect or result.blank != result.total:
        raise ValueError('Pristine Trainer Check failed')


def _exchange_directories(staged: Path, current: Path):
    """One filesystem transaction: readers see either complete generation.

    Fail closed on platforms without directory exchange; no delete/rename gap.
    After exchange staged contains the old generation, removed by TemporaryDirectory.
    """
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == 'darwin':
        fn = libc.renamex_np
        fn.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        result = fn(os.fsencode(staged), os.fsencode(current), 2)  # RENAME_SWAP
    elif sys.platform.startswith('linux') and hasattr(libc, 'renameat2'):
        fn = libc.renameat2
        fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        result = fn(-100, os.fsencode(staged), -100, os.fsencode(current), 2)
    else:
        raise ValueError('Atomic directory replacement is unsupported on this platform')
    if result:
        number = ctypes.get_errno()
        raise OSError(number, os.strerror(number))


def build_company(company: Company, assumptions=None):
    from .engine.reference_model import ReferenceModelBuilder
    from .trainer.workbook import build_training_workbook
    from .build_status import status_rows
    from .trainer.semantic_io import load_semantic_map
    current = company.output
    from .__main__ import _validate_build_output
    _validate_build_output(company.trainer, [])
    if current.is_symlink():
        raise ValueError('Current build directory must not be a symlink')
    current.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f'.{company.name}-staging-', dir=current.parent) as raw:
        staged = Path(raw)
        fin = prepare_company_input(company, staged)
        trainer, answer = build_training_workbook(fin, staged / company.trainer.name, assumptions, current_snapshot=True)
        verify_staged(fin, trainer, answer, assumptions)
        rows = status_rows(load_semantic_map(answer))
        _write_json(staged / 'build_status.json', rows)
        if current.exists():
            _exchange_directories(staged, current)
        else:
            os.rename(staged, current)
    # Retire only recognizable legacy workbook artifacts for this company.
    # Canonical-directory contents were replaced as a single generation above.
    pattern = re.compile(re.escape(company.name) + r'(?:_(?:Live|KPI|Preview|[0-9][0-9_-]*))?_(?:Trainer|Answer_Key)\.(?:xlsx|component_map\.json|assumptions\.json|trainer\.json)$')
    for legacy in current.parent.iterdir():
        if pattern.fullmatch(legacy.name) and legacy.is_file():
            try:
                legacy.unlink()
            except OSError as exc:
                print(f'warning: built successfully but could not retire {legacy}: {exc}', file=sys.stderr)
    return rows
