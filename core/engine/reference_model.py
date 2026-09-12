"""Build the complete reference BAV workbook and semantic component map."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from ..data.interface import LineItem, StandardizedFinancials
from ..data.line_identity import line_identity
from ..model.classification import BALANCE_SHEET_CATEGORIES
from ..model.financial_math import compute_anchor
from ..model.earnings_quality import (
    compute_earnings_quality_series,
    earnings_quality_availability,
)
from ..model.judgment import JudgmentCase, classification_judgment_cases
from ..model.line_resolver import resolve_line, workbook_row_for
from ..model.normalization import (
    NormalizationCase,
    compute_normalization_series,
    normalization_cases,
)
from ..model.period_axis import canonical_fiscal_periods
from ..model.profitability_drivers import compute_profitability_driver_series
from ..model.ri_engine import run_scenario, weighted_ivps
from ..model.working_capital import (
    compute_working_capital_series,
    working_capital_applicable,
)
from .component_catalog import (
    DEFERRED_COMPONENT_SPECS,
    expand_historical_specs,
    expand_normalization_specs,
    expand_profitability_driver_specs,
    expand_quality_specs,
    expand_working_capital_specs,
)
from .map_embed import embed_component_map_sheet
from .semantic_map import SemanticMap

NUM_FMT = "#,##0;(#,##0)"
PCT_FMT = "0.0%"
SOURCE_START_ROW = 7
BLUE = Font(color="0000FF")
BOLD = Font(bold=True)
ORANGE = PatternFill("solid", start_color="FCE5CD")
YELLOW = PatternFill("solid", start_color="FFF2CC")
GREEN = PatternFill("solid", start_color="D9EAD3")
PRACTICE_YELLOW = PatternFill("solid", start_color="FFFF00")

DEFERRED_TAB_NAMES = ("Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary")
DEFERRED_PLACEHOLDER = "Deferred from historical-only v1"

JUDGMENT_SHEET = "Accounting Judgment"
NORMALIZATION_JUDGMENT_SHEET = "Normalization Judgment"
EARNINGS_NORMALIZATION_SHEET = "Earnings Normalization"
EARNINGS_QUALITY_SHEET = "Earnings Quality"
WORKING_CAPITAL_SHEET = "Working Capital Analysis"
JUDGMENT_INSTRUCTION = (
    "The supplied treatment is the model's reference treatment, not a universal "
    "accounting truth. Compare it with the listed alternative(s), choose the "
    "treatment you would defend, and explain the economic consequence."
)
JUDGMENT_STEP_NOTE = (
    "Choose a treatment in column F only. That choice drives the matching Condensed "
    "Financials classification and downstream historical schedules; leaving F blank "
    "uses the supplied reference treatment. Columns D:E are display context and must "
    "not be edited. Enter your rationale and economic consequence in G:H. Formula Check "
    "grades formula cells against the treatment currently selected in F and validates "
    "that the generated classification links remain intact; it does not grade the "
    "judgment response itself. Do not edit the linked Condensed Financials "
    "classification cell directly."
)
NORMALIZATION_JUDGMENT_INSTRUCTION = (
    "The supplied treatment is the model's reference convention, not a universal "
    "truth. Decide whether each supplied candidate should remain in recurring "
    "earnings or be normalized out."
)
NORMALIZATION_JUDGMENT_STEP_NOTE = (
    "Choose the treatment in column F. Blank F uses the supplied reference treatment. "
    "G:H are ungraded reasoning. Do not edit the generated Earnings Normalization "
    "treatment link directly."
)


class ReferenceModelBuilder:
    """Construct reference workbook and populate SemanticMap at build time."""

    def __init__(
        self,
        financials: StandardizedFinancials,
        assumptions: dict[str, Any] | None = None,
        *,
        include_deferred_forecast: bool = False,
    ):
        self.fin = financials
        self.periods = canonical_fiscal_periods(financials)
        self.include_deferred_forecast = include_deferred_forecast
        self.assumptions = dict(assumptions or {})
        self.assumptions.setdefault("classificationOverrides", {})
        self.assumptions.setdefault("normalizationCandidates", [])
        self.rowmap: dict[str, Any] = {}
        self.historical_specs = expand_historical_specs(self.periods)
        overrides = self.assumptions.get("classificationOverrides") or {}
        self.anchor = compute_anchor(
            financials,
            self.periods,
            classification_overrides=overrides,
        )
        self.judgment_cases: tuple[JudgmentCase, ...] = classification_judgment_cases(
            self.fin,
            self.periods,
            self.anchor.reformulation,
        )
        self.normalization_cases: tuple[NormalizationCase, ...] = normalization_cases(
            self.fin,
            self.periods,
            self.assumptions,
        )
        self.normalization_specs = (
            expand_normalization_specs(
                self.periods,
                start_order=len(self.historical_specs) + 1,
            )
            if self.normalization_cases
            else ()
        )
        self.quality_availability = earnings_quality_availability(self.fin)
        if self.quality_availability.operating_cash_flow:
            self.quality_series = compute_earnings_quality_series(
                self.fin,
                self.periods,
                self.anchor,
            )
            self.quality_specs = expand_quality_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs) + len(self.normalization_specs) + 1
                ),
                include_asset_scaled=self.quality_availability.total_assets,
            )
        else:
            self.quality_series = None
            self.quality_specs = ()
        if working_capital_applicable(self.anchor):
            self.working_capital_series = compute_working_capital_series(self.anchor)
            self.working_capital_specs = expand_working_capital_specs(
                self.periods,
                start_order=(
                    len(self.historical_specs)
                    + len(self.normalization_specs)
                    + len(self.quality_specs)
                    + 1
                ),
            )
        else:
            self.working_capital_series = None
            self.working_capital_specs = ()
        self.profitability_driver_series = compute_profitability_driver_series(self.anchor)
        self.profitability_driver_specs = expand_profitability_driver_specs(
            self.periods,
            start_order=(
                len(self.historical_specs)
                + len(self.normalization_specs)
                + len(self.quality_specs)
                + len(self.working_capital_specs)
                + 1
            ),
        )
        self.expected_specs = (
            self.historical_specs
            + self.normalization_specs
            + self.quality_specs
            + self.working_capital_specs
            + self.profitability_driver_specs
        )
        self.semantic_map = SemanticMap(expected_specs=self.expected_specs)
        self._historical_spec_index = {
            (s.family_id, s.period_index): s for s in self.historical_specs
        }
        self._normalization_spec_index = {
            (s.family_id, s.period_index): s for s in self.normalization_specs
        }
        self._quality_spec_index = {
            (s.family_id, s.period_index): s for s in self.quality_specs
        }
        self._working_capital_spec_index = {
            (s.family_id, s.period_index): s for s in self.working_capital_specs
        }
        self._profitability_driver_spec_index = {
            (s.family_id, s.period_index): s for s in self.profitability_driver_specs
        }
        self._deferred_spec_index = {c.id: c for c in DEFERRED_COMPONENT_SPECS}
        self.normalization_series = (
            compute_normalization_series(
                self.fin,
                self.periods,
                self.anchor,
                self.normalization_cases,
            )
            if self.normalization_cases
            else None
        )
        self._judgment_row_by_identity = {
            case.line_identity: 4 + case.order
            for case in self.judgment_cases
        }
        self._judgment_case_by_identity = {
            case.line_identity: case for case in self.judgment_cases
        }
        self._n = len(self.periods)
        self._last_fy_col = 2 + self._n - 1
        self._first_fc_col = 2 + self._n
        self._scenario_results: dict[str, Any] = {}
        self._base_result = None

        if self.include_deferred_forecast:
            # Internal/legacy path only — never enabled by normal v1 build.
            if "scenarios" not in self.assumptions or "marketData" not in self.assumptions:
                defaults = self._default_assumptions()
                for key, value in defaults.items():
                    self.assumptions.setdefault(key, value)
            shares = self.assumptions["marketData"]["dilutedShares"]
            self._scenario_results = {
                name: run_scenario(
                    self.assumptions["scenarios"][name],
                    self.anchor,
                    shares,
                )
                for name in ("Bear", "Base", "Bull")
            }
            self._base_result = self._scenario_results["Base"]

    def _default_assumptions(self) -> dict[str, Any]:
        anchor_rev = 1000.0
        if self.fin.income_statement and self.periods:
            rev_item = resolve_line(
                self.fin.income_statement, "revenue", required=True
            ).item
            assert rev_item is not None
            anchor_rev = rev_item.values.get(self.periods[-1]) or 1000.0
        growth = [0.10] * 10
        margin = [0.15] * 10
        nowc = [0.05] * 10
        nola = [0.50] * 10
        return {
            "schemaVersion": 2,
            "ticker": self.fin.ticker,
            "company": self.fin.company_name,
            "marketData": {
                "price": 50.0,
                "priceDate": date.today().isoformat(),
                "dilutedShares": 1000.0,
                "riskFreeRate": 0.04,
                "equityRiskPremium": 0.05,
            },
            "scenarios": {
                name: {
                    "probability": prob,
                    "beta": beta,
                    "costOfEquity": 0.04 + beta * 0.05,
                    "taxRate": 0.165,
                    "terminalGrowth": 0.03,
                    "growthVector": growth,
                    "marginVector": margin,
                    "nowcRatioVector": nowc,
                    "nolaRatioVector": nola,
                }
                for name, prob, beta in (
                    ("Bear", 0.25, 1.3),
                    ("Base", 0.50, 1.15),
                    ("Bull", 0.25, 1.05),
                )
            },
            "classificationOverrides": {},
            "meta": {"anchorRevenue": anchor_rev, "currency": self.fin.units},
        }

    def build(self, output_path: Path) -> SemanticMap:
        wb = Workbook()
        self._build_source_tabs(wb)
        self._build_condensed(wb)
        self._build_dupont(wb)
        self._build_accounting_judgment(wb)
        if self.normalization_cases:
            self._build_normalization_judgment(wb)
            self._build_earnings_normalization(wb)
        if self.quality_series is not None:
            self._build_earnings_quality(wb)
        if self.working_capital_series is not None:
            self._build_working_capital_analysis(wb)
        if self.include_deferred_forecast:
            for scenario in ("Bear", "Base", "Bull"):
                self._build_model_tab(wb, scenario)
            self._build_scenario_summary(wb)
        else:
            for name in DEFERRED_TAB_NAMES:
                ws = wb.create_sheet(name)
                ws["A1"] = DEFERRED_PLACEHOLDER
                ws.sheet_state = "hidden"

        errors = self.semantic_map.validate_complete()
        if errors:
            raise ValueError("Component map validation failed:\n" + "\n".join(errors))

        embed_component_map_sheet(wb, self.semantic_map)
        from ..trainer.check_context import build_check_context, embed_check_context_sheet

        context = build_check_context(
            self.fin,
            self.periods,
            self.assumptions,
            self.judgment_cases,
            self.normalization_cases,
        )
        embed_check_context_sheet(wb, context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)

        sidecar = output_path.with_suffix(".component_map.json")
        self.semantic_map.save_json(sidecar)
        assumptions_path = output_path.with_suffix(".assumptions.json")
        assumptions_path.write_text(json.dumps(self.assumptions, indent=2) + "\n", encoding="utf-8")
        rowmap_path = output_path.parent / "rowmap.json"
        rowmap_path.write_text(
            json.dumps({**self.rowmap, **self.semantic_map.rowmap}, indent=2) + "\n",
            encoding="utf-8",
        )
        return self.semantic_map

    def _col(self, idx: int) -> str:
        return get_column_letter(idx)

    def _register_historical(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._historical_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_normalization(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._normalization_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_quality(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._quality_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_working_capital(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._working_capital_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_profitability_driver(
        self,
        family_id: str,
        period_index: int,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = self._profitability_driver_spec_index[(family_id, period_index)]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _register_deferred(
        self,
        spec_id: str,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        if spec_id not in self._deferred_spec_index:
            raise KeyError(f"Unknown deferred component spec: {spec_id}")
        spec = self._deferred_spec_index[spec_id]
        self.semantic_map.register(
            spec, tab, row, col, formula, expected, related_cells=related
        )

    def _resolved_source_row(self, items: list[LineItem], concept: str, *, required: bool = False) -> int | None:
        """Workbook row for a canonical concept — same LineItem as compute_anchor()."""
        return workbook_row_for(
            resolve_line(items, concept, required=required),
            start_row=SOURCE_START_ROW,
        )

    def _header_block(self, ws, statement: str) -> None:
        ws["A1"] = f"Company: {self.fin.company_name} ({self.fin.ticker})"
        ws["A2"] = f"Statement: {statement}"
        ws["A3"] = f"Units: {self.fin.units}"
        ws["A4"] = f"Source: manual ingestion ({self.fin.jurisdiction})"
        ws["A6"] = "Line Item"
        ws["A6"].font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=6, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        ws.column_dimensions["A"].width = 48
        for j in range(self._n):
            ws.column_dimensions[self._col(2 + j)].width = 16

    def _fill_statement(self, ws, items: list[LineItem], start_row: int = 7) -> int:
        r = start_row
        sheet = ws.title
        for item in items:
            ws.cell(row=r, column=1, value=item.label)
            for j, pd in enumerate(self.periods):
                val = item.values.get(pd)
                c = ws.cell(row=r, column=2 + j, value=val)
                c.number_format = NUM_FMT
            self.rowmap[f"{sheet}!{line_identity(item).key()}"] = r
            r += 1
        return r

    def _build_source_tabs(self, wb: Workbook) -> None:
        ws = wb.active
        ws.title = "Income Statement"
        self._header_block(ws, "Income Statement")
        self._fill_statement(ws, self.fin.income_statement)
        ws = wb.create_sheet("Balance Sheet")
        self._header_block(ws, "Balance Sheet")
        self._fill_statement(ws, self.fin.balance_sheet)
        ws = wb.create_sheet("Cash Flow Statement")
        self._header_block(ws, "Cash Flow Statement")
        self._fill_statement(ws, self.fin.cash_flow)

    def _build_condensed(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Condensed Financials")
        ws["A1"] = f"{self.fin.company_name} ({self.fin.ticker}) — Condensed Financials"
        ws.column_dimensions["A"].width = 42
        ws.column_dimensions["B"].width = 32

        r = 4
        ws.cell(row=r, column=1, value="BALANCE SHEET CLASSIFICATION").font = BOLD
        r += 1
        ws.cell(row=r, column=1, value="Line Item").font = BOLD
        ws.cell(row=r, column=2, value="Classification").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r, column=3 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
            ws.column_dimensions[self._col(3 + j)].width = 14
        r += 1

        notes_col = 3 + self._n
        ws.cell(row=r - 1, column=notes_col, value="Notes").font = BOLD
        ws.column_dimensions[self._col(notes_col)].width = 42

        class_start = r
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(BALANCE_SHEET_CATEGORIES)}"',
            allow_blank=False,
        )
        ws.add_data_validation(dv)
        # Shared decisions drive defaults; SUMIF stays on-sheet for live reclassification.
        reform = self.anchor.reformulation
        for idx in reform.detail_indices:
            item = self.fin.balance_sheet[idx]
            decision = reform.decisions[idx]
            identity = line_identity(item).key()
            ws.cell(row=r, column=1, value=item.label)
            judgment_case = self._judgment_case_by_identity.get(identity)
            if judgment_case is not None:
                # Non-practice formula: learner edits Accounting Judgment!F only.
                from ..trainer.check_context import live_classification_formula

                formula = live_classification_formula(
                    4 + judgment_case.order,
                    judgment_case.supplied_treatment,
                )
                ws.cell(row=r, column=2, value=formula)
            else:
                cat_cell = ws.cell(row=r, column=2, value=decision.category)
                dv.add(cat_cell)
            for j, pd in enumerate(self.periods):
                c = ws.cell(row=r, column=3 + j, value=item.values.get(pd))
                c.number_format = NUM_FMT
            note_parts: list[str] = []
            if decision.ambiguous:
                note_parts.append(f"⚠ Review: {decision.reason or 'judgment required'}")
            if decision.overridden:
                note_parts.append(f"Override → {decision.category}")
            if note_parts:
                ws.cell(row=r, column=notes_col, value="; ".join(note_parts))
            r += 1
        class_end = r - 1
        self.rowmap["condensed_class_start"] = class_start
        self.rowmap["condensed_class_end"] = class_end
        self.rowmap["condensed_class_value_col0"] = 3

        r += 1
        ws.cell(row=r, column=1, value="CONDENSED INCOME STATEMENT").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        r += 1

        ni_src = self._resolved_source_row(self.fin.income_statement, "net_income", required=True)
        rev_src = self._resolved_source_row(self.fin.income_statement, "revenue", required=True)
        pretax_src = self._resolved_source_row(
            self.fin.income_statement, "pretax_income", required=True
        )
        tax_src = self._resolved_source_row(
            self.fin.income_statement, "tax_expense", required=True
        )
        int_exp_src = self._resolved_source_row(
            self.fin.income_statement, "interest_expense", required=True
        )
        int_inc_src = self._resolved_source_row(
            self.fin.income_statement, "interest_income", required=True
        )
        equity_src = self._resolved_source_row(self.fin.balance_sheet, "total_equity")
        row_nums: dict[str, int] = {}
        hist = self.anchor.historical
        for label, src_row, bold, family_id, expected_series in [
            ("Revenue", rev_src, False, "revenue_link", hist.revenue),
            ("Net Income", ni_src, False, "net_income_link", hist.net_income),
            ("Pretax Income", pretax_src, False, None, None),
            ("Tax Expense", tax_src, False, None, None),
            ("Interest Expense", int_exp_src, False, None, None),
            ("Interest Income", int_inc_src, False, None, None),
        ]:
            assert src_row is not None
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            for j in range(self._n):
                col = self._col(2 + j)
                formula = f"='Income Statement'!{col}{src_row}"
                ws.cell(row=r, column=2 + j, value=formula)
                if family_id is not None and expected_series is not None:
                    self._register_historical(
                        family_id,
                        j,
                        "Condensed Financials",
                        r,
                        2 + j,
                        formula,
                        expected_series[j],
                    )
            row_nums[label] = r
            if label == "Net Income":
                self.rowmap["condensed_ni_row"] = r
            if label == "Revenue":
                self.rowmap["condensed_revenue_row"] = r
            r += 1

        etr_row = r
        ws.cell(row=r, column=1, value="Effective Tax Rate")
        pretax_r = row_nums["Pretax Income"]
        tax_r = row_nums["Tax Expense"]
        for j in range(self._n):
            col = self._col(2 + j)
            formula = f"=IF({col}{pretax_r}=0,NA(),-{col}{tax_r}/{col}{pretax_r})"
            ws.cell(row=r, column=2 + j, value=formula).number_format = PCT_FMT
            self._register_historical(
                "effective_tax_rate_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                formula,
                hist.effective_tax_rate[j],
            )
        row_nums["Effective Tax Rate"] = etr_row
        self.rowmap["condensed_etr_row"] = etr_row
        r += 1

        # Net interest uses explicitly supplied Interest Expense and Interest Income.
        net_int_row = r
        ws.cell(row=r, column=1, value="Net Interest")
        for j in range(self._n):
            col = self._col(2 + j)
            f = (
                f"=-({col}{row_nums['Interest Expense']}"
                f"+{col}{row_nums['Interest Income']})"
            )
            ws.cell(row=r, column=2 + j, value=f).number_format = NUM_FMT
            self._register_historical(
                "net_interest_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                f,
                hist.net_interest[j],
            )
        row_nums["Net Interest"] = net_int_row
        r += 1

        niat_row = r
        ws.cell(row=r, column=1, value="Net Interest After Tax")
        for j in range(self._n):
            col = self._col(2 + j)
            formula = (
                f"=IF({col}{net_int_row}=0,0,"
                f"IF(ISNA({col}{etr_row}),NA(),{col}{net_int_row}*(1-{col}{etr_row})))"
            )
            ws.cell(row=r, column=2 + j, value=formula).number_format = NUM_FMT
            self._register_historical(
                "net_interest_after_tax_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                formula,
                hist.net_interest_after_tax[j],
            )
        row_nums["Net Interest After Tax"] = niat_row
        self.rowmap["condensed_niat_row"] = niat_row
        r += 1

        nopat_row = r
        ws.cell(row=r, column=1, value="NOPAT").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            formula = f"={col}{row_nums['Net Income']}+{col}{niat_row}"
            c = ws.cell(row=r, column=2 + j, value=formula)
            c.fill = GREEN
            c.number_format = NUM_FMT
            self._register_historical(
                "nopat_fy",
                j,
                "Condensed Financials",
                r,
                2 + j,
                formula,
                hist.nopat[j],
            )
        r += 1
        self.rowmap["condensed_nopat_row"] = nopat_row

        r += 1
        ws.cell(row=r, column=1, value="CONDENSED BALANCE SHEET").font = BOLD
        r += 1

        def _class_sumif(category: str, value_col: str) -> str:
            return (
                f'SUMIF($B${class_start}:$B${class_end},"{category}",'
                f"{value_col}${class_start}:{value_col}${class_end})"
            )

        def _fill_sumif_row(label: str, category: str, *, bold: bool = False) -> int:
            nonlocal r
            row = r
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            for j in range(self._n):
                vcol = self._col(3 + j)
                formula = f"={_class_sumif(category, vcol)}"
                c = ws.cell(row=r, column=2 + j, value=formula)
                c.number_format = NUM_FMT
            r += 1
            return row

        cat_totals = self.anchor.reformulation.category_totals
        reform = self.anchor.reformulation

        def _register_all_periods(
            family_id: str, row: int, expected_series: list[float]
        ) -> None:
            for j in range(self._n):
                self._register_historical(
                    family_id,
                    j,
                    "Condensed Financials",
                    row,
                    2 + j,
                    str(ws.cell(row=row, column=2 + j).value),
                    expected_series[j],
                )

        owca_row = _fill_sumif_row(
            "Operating Working Capital Assets", "Operating Working Capital Asset"
        )
        _register_all_periods(
            "owca_agg", owca_row, cat_totals["Operating Working Capital Asset"]
        )
        owcl_row = _fill_sumif_row(
            "Operating Working Capital Liabilities",
            "Operating Working Capital Liability",
        )
        _register_all_periods(
            "owcl_agg", owcl_row, cat_totals["Operating Working Capital Liability"]
        )

        nowc_row = r
        ws.cell(row=r, column=1, value="NOWC").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{owca_row}-{col}{owcl_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("nowc_agg", nowc_row, list(reform.nowc))

        olta_row = _fill_sumif_row(
            "Operating Long-Term Assets", "Operating Long-Term Asset"
        )
        _register_all_periods(
            "olta_agg", olta_row, cat_totals["Operating Long-Term Asset"]
        )
        oltl_row = _fill_sumif_row(
            "Operating Long-Term Liabilities", "Operating Long-Term Liability"
        )
        _register_all_periods(
            "oltl_agg", oltl_row, cat_totals["Operating Long-Term Liability"]
        )

        nola_row = r
        ws.cell(row=r, column=1, value="NOLA").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{olta_row}-{col}{oltl_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("nola_agg", nola_row, list(reform.nola))

        noa_row = r
        ws.cell(row=r, column=1, value="NOA").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{nowc_row}+{col}{nola_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("noa_agg", noa_row, list(reform.noa))

        fa_row = _fill_sumif_row("Financial Assets", "Financial Asset")
        _register_all_periods("financial_assets_agg", fa_row, cat_totals["Financial Asset"])
        fl_row = _fill_sumif_row("Financial Liabilities", "Financial Liability")
        _register_all_periods(
            "financial_liabilities_agg", fl_row, cat_totals["Financial Liability"]
        )

        nd_row = r
        ws.cell(row=r, column=1, value="Net Debt").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{fl_row}-{col}{fa_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods("net_debt", nd_row, list(reform.net_debt))

        equity_row = r
        ws.cell(row=r, column=1, value="Equity (NOA - Net Debt)").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{noa_row}-{col}{nd_row}")
            c.number_format = NUM_FMT
        r += 1
        _register_all_periods(
            "equity_reformulated_fy", equity_row, list(reform.implied_equity)
        )

        reported_eq_row = r
        ws.cell(row=r, column=1, value="Reported Equity").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            if equity_src:
                f: str | None = f"='Balance Sheet'!{col}{equity_src}"
            else:
                f = None
            c = ws.cell(row=r, column=2 + j, value=f)
            c.number_format = NUM_FMT
        r += 1

        total_cap_row = r
        ws.cell(row=r, column=1, value="Total Capital").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            c = ws.cell(row=r, column=2 + j, value=f"={col}{nd_row}+{col}{equity_row}")
            c.number_format = NUM_FMT
        r += 1

        check_row = r
        ws.cell(row=r, column=1, value="CHECK").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            if equity_src:
                f = (
                    f'=IF(ABS({col}{equity_row}-{col}{reported_eq_row})<1,"OK","CHECK")'
                )
            else:
                f = '="UNVERIFIED"'
            ws.cell(row=r, column=2 + j, value=f)
        r += 1

        self.rowmap["condensed_owca_row"] = owca_row
        self.rowmap["condensed_owcl_row"] = owcl_row
        self.rowmap["condensed_nowc_row"] = nowc_row
        self.rowmap["condensed_nola_row"] = nola_row
        self.rowmap["condensed_noa_row"] = noa_row
        self.rowmap["condensed_nd_row"] = nd_row
        self.rowmap["condensed_equity_row"] = equity_row
        self.rowmap["condensed_reported_equity_row"] = reported_eq_row
        self.rowmap["condensed_total_capital_row"] = total_cap_row
        self.rowmap["condensed_check_row"] = check_row
        self.rowmap["condensed_nola_via_noa"] = True

    def _build_dupont(self, wb: Workbook) -> None:
        ws = wb.create_sheet("ALT DuPont")
        ws["A1"] = f"{self.fin.company_name} — DuPont Decomposition"
        ws["A2"] = "ROE = RNOA + FLEV × Spread"
        ws.column_dimensions["A"].width = 42
        r_hdr = 4
        ws.cell(row=r_hdr, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r_hdr, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        nopat_r = self.rowmap["condensed_nopat_row"]
        niat_r = self.rowmap["condensed_niat_row"]
        noa_r = self.rowmap["condensed_noa_row"]
        nd_r = self.rowmap["condensed_nd_row"]
        eq_r = self.rowmap["condensed_equity_row"]
        ni_r = self.rowmap["condensed_ni_row"]
        rev_r = self.rowmap["condensed_revenue_row"]

        metrics = [
            "Sales Growth",
            "NOPAT Margin",
            "RNOA",
            "After-tax CoD",
            "Spread",
            "FLEV",
            "ROE (decomposed)",
            "Actual ROE",
        ]
        metric_rows: dict[str, int] = {}
        r = r_hdr + 1
        for metric in metrics:
            ws.cell(row=r, column=1, value=metric)
            metric_rows[metric] = r
            r += 1

        sales_row = metric_rows["Sales Growth"]
        margin_row = metric_rows["NOPAT Margin"]
        rnoa_row = metric_rows["RNOA"]
        cod_row = metric_rows["After-tax CoD"]
        spread_row = metric_rows["Spread"]
        flev_row = metric_rows["FLEV"]
        roe_row = metric_rows["ROE (decomposed)"]
        actual_row = metric_rows["Actual ROE"]

        dup = self.anchor.dupont
        na = "N/A"

        for j in range(self._n):
            out_col_idx = 2 + j
            out_col = self._col(out_col_idx)
            src_col = self._col(2 + j)
            src_prev = self._col(2 + j - 1) if j > 0 else None

            # NOPAT Margin — all periods
            margin_f = (
                f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                f"'Condensed Financials'!{src_col}{nopat_r}/"
                f"'Condensed Financials'!{src_col}{rev_r})"
            )
            cell = ws.cell(row=margin_row, column=out_col_idx, value=margin_f)
            cell.number_format = PCT_FMT
            self._register_historical(
                "nopat_margin",
                j,
                "ALT DuPont",
                margin_row,
                out_col_idx,
                margin_f,
                dup["NOPAT Margin"][j],
            )

            if j == 0:
                for row in (
                    sales_row,
                    rnoa_row,
                    cod_row,
                    spread_row,
                    flev_row,
                    roe_row,
                    actual_row,
                ):
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            assert src_prev is not None
            sales_f = (
                f"=IF('Condensed Financials'!{src_prev}{rev_r}=0,NA(),"
                f"'Condensed Financials'!{src_col}{rev_r}/"
                f"'Condensed Financials'!{src_prev}{rev_r}-1)"
            )
            ws.cell(row=sales_row, column=out_col_idx, value=sales_f).number_format = PCT_FMT
            self._register_historical(
                "sales_growth",
                j,
                "ALT DuPont",
                sales_row,
                out_col_idx,
                sales_f,
                dup["Sales Growth"][j],
            )

            rnoa_f = (
                f"=IF((('Condensed Financials'!{src_col}{noa_r}+"
                f"'Condensed Financials'!{src_prev}{noa_r})/2)=0,NA(),"
                f"'Condensed Financials'!{src_col}{nopat_r}/"
                f"(('Condensed Financials'!{src_col}{noa_r}+"
                f"'Condensed Financials'!{src_prev}{noa_r})/2))"
            )
            ws.cell(row=rnoa_row, column=out_col_idx, value=rnoa_f).number_format = PCT_FMT
            self._register_historical(
                "rnoa",
                j,
                "ALT DuPont",
                rnoa_row,
                out_col_idx,
                rnoa_f,
                dup["RNOA"][j],
            )

            cod_f = (
                f"=IF((('Condensed Financials'!{src_col}{nd_r}+"
                f"'Condensed Financials'!{src_prev}{nd_r})/2)=0,NA(),"
                f"'Condensed Financials'!{src_col}{niat_r}/"
                f"(('Condensed Financials'!{src_col}{nd_r}+"
                f"'Condensed Financials'!{src_prev}{nd_r})/2))"
            )
            ws.cell(row=cod_row, column=out_col_idx, value=cod_f).number_format = PCT_FMT
            self._register_historical(
                "after_tax_cod",
                j,
                "ALT DuPont",
                cod_row,
                out_col_idx,
                cod_f,
                dup["After-tax CoD"][j],
            )

            spread_f = f"={out_col}{rnoa_row}-{out_col}{cod_row}"
            ws.cell(row=spread_row, column=out_col_idx, value=spread_f).number_format = PCT_FMT
            self._register_historical(
                "spread",
                j,
                "ALT DuPont",
                spread_row,
                out_col_idx,
                spread_f,
                dup["Spread"][j],
            )

            flev_f = (
                f"=IF((('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2)=0,NA(),"
                f"(('Condensed Financials'!{src_col}{nd_r}+"
                f"'Condensed Financials'!{src_prev}{nd_r})/2)/"
                f"(('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2))"
            )
            ws.cell(row=flev_row, column=out_col_idx, value=flev_f)
            self._register_historical(
                "flev",
                j,
                "ALT DuPont",
                flev_row,
                out_col_idx,
                flev_f,
                dup["FLEV"][j],
            )

            roe_f = f"={out_col}{rnoa_row}+{out_col}{flev_row}*({out_col}{spread_row})"
            ws.cell(row=roe_row, column=out_col_idx, value=roe_f).number_format = PCT_FMT
            self._register_historical(
                "roe_decomp",
                j,
                "ALT DuPont",
                roe_row,
                out_col_idx,
                roe_f,
                dup["ROE (decomposed)"][j],
            )

            actual_f = (
                f"=IF((('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2)=0,NA(),"
                f"'Condensed Financials'!{src_col}{ni_r}/"
                f"(('Condensed Financials'!{src_col}{eq_r}+"
                f"'Condensed Financials'!{src_prev}{eq_r})/2))"
            )
            ws.cell(row=actual_row, column=out_col_idx, value=actual_f).number_format = PCT_FMT
            self._register_historical(
                "actual_roe",
                j,
                "ALT DuPont",
                actual_row,
                out_col_idx,
                actual_f,
                dup["Actual ROE"][j],
            )

        # RNOA margin / turnover driver decomposition (Step 9C.1)
        drivers = self.profitability_driver_series
        driver_section_row = actual_row + 2
        average_noa_row = driver_section_row + 1
        turnover_row = driver_section_row + 2
        intensity_row = driver_section_row + 3
        driver_rnoa_row = driver_section_row + 4
        driver_check_row = driver_section_row + 5

        ws.cell(
            row=driver_section_row, column=1, value="RNOA DRIVER DECOMPOSITION"
        ).font = BOLD
        ws.cell(row=average_noa_row, column=1, value="Average NOA")
        ws.cell(row=turnover_row, column=1, value="NOA Turnover")
        ws.cell(row=intensity_row, column=1, value="NOA Intensity")
        ws.cell(row=driver_rnoa_row, column=1, value="RNOA from Margin × Turnover")
        ws.cell(row=driver_check_row, column=1, value="RNOA DRIVER CHECK").font = BOLD

        for j in range(self._n):
            out_col_idx = 2 + j
            out_col = self._col(out_col_idx)
            src_col = self._col(2 + j)
            if j == 0:
                for row in (
                    average_noa_row,
                    turnover_row,
                    intensity_row,
                    driver_rnoa_row,
                    driver_check_row,
                ):
                    ws.cell(row=row, column=out_col_idx, value=na)
                continue

            src_prev = self._col(2 + j - 1)
            average_f = (
                f"=('Condensed Financials'!{src_prev}{noa_r}+"
                f"'Condensed Financials'!{src_col}{noa_r})/2"
            )
            turnover_f = (
                f"=IF({out_col}{average_noa_row}=0,NA(),"
                f"'Condensed Financials'!{src_col}{rev_r}/{out_col}{average_noa_row})"
            )
            intensity_f = (
                f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
                f"{out_col}{average_noa_row}/'Condensed Financials'!{src_col}{rev_r})"
            )
            driver_rnoa_f = f"={out_col}{margin_row}*{out_col}{turnover_row}"
            driver_check = (
                f'=IF(ISNA({out_col}{driver_rnoa_row}),"N/A",'
                f'IF(ISNA({out_col}{rnoa_row}),"CHECK",'
                f'IF(ABS({out_col}{driver_rnoa_row}-{out_col}{rnoa_row})<0.0000001,'
                f'"OK","CHECK")))'
            )

            c = ws.cell(row=average_noa_row, column=out_col_idx, value=average_f)
            c.number_format = NUM_FMT
            c = ws.cell(row=turnover_row, column=out_col_idx, value=turnover_f)
            c.number_format = "0.00x"
            c = ws.cell(row=intensity_row, column=out_col_idx, value=intensity_f)
            c.number_format = "0.00x"
            c = ws.cell(row=driver_rnoa_row, column=out_col_idx, value=driver_rnoa_f)
            c.number_format = PCT_FMT
            ws.cell(row=driver_check_row, column=out_col_idx, value=driver_check)

            assert drivers.average_noa[j] is not None
            self._register_profitability_driver(
                "average_noa",
                j,
                "ALT DuPont",
                average_noa_row,
                out_col_idx,
                average_f,
                float(drivers.average_noa[j]),
            )
            turnover_expected = drivers.noa_turnover[j]
            assert turnover_expected is not None
            self._register_profitability_driver(
                "noa_turnover",
                j,
                "ALT DuPont",
                turnover_row,
                out_col_idx,
                turnover_f,
                turnover_expected
                if isinstance(turnover_expected, str)
                else float(turnover_expected),
            )
            intensity_expected = drivers.noa_intensity[j]
            assert intensity_expected is not None
            self._register_profitability_driver(
                "noa_intensity",
                j,
                "ALT DuPont",
                intensity_row,
                out_col_idx,
                intensity_f,
                intensity_expected
                if isinstance(intensity_expected, str)
                else float(intensity_expected),
            )
            driver_expected = drivers.rnoa_from_margin_turnover[j]
            assert driver_expected is not None
            self._register_profitability_driver(
                "rnoa_margin_turnover",
                j,
                "ALT DuPont",
                driver_rnoa_row,
                out_col_idx,
                driver_rnoa_f,
                driver_expected
                if isinstance(driver_expected, str)
                else float(driver_expected),
            )

        self.rowmap["dupont_average_noa_row"] = average_noa_row
        self.rowmap["dupont_noa_turnover_row"] = turnover_row
        self.rowmap["dupont_noa_intensity_row"] = intensity_row
        self.rowmap["dupont_driver_rnoa_row"] = driver_rnoa_row
        self.rowmap["dupont_driver_check_row"] = driver_check_row

    def _build_accounting_judgment(self, wb: Workbook) -> None:
        ws = wb.create_sheet(JUDGMENT_SHEET)
        ws["A1"] = "Accounting Judgment"
        ws["A1"].font = BOLD
        ws["A2"] = JUDGMENT_INSTRUCTION
        ws["A3"] = JUDGMENT_STEP_NOTE
        headers = [
            "Order",
            "Line item",
            "Topic",
            "Supplied reference treatment",
            "Alternative(s) to evaluate",
            "Treatment to defend",
            "Rationale",
            "Economic consequence",
        ]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col, value=header)
            cell.font = BOLD
        widths = (8, 32, 36, 28, 32, 28, 40, 44)
        for idx, width in enumerate(widths, start=1):
            ws.column_dimensions[self._col(idx)].width = width

        if not self.judgment_cases:
            ws.cell(
                row=5,
                column=1,
                value=(
                    "No supported guided classification judgments were identified "
                    "from the supplied company data."
                ),
            )
            return

        for case in self.judgment_cases:
            row = 4 + case.order
            options = (case.supplied_treatment,) + case.alternatives
            ws.cell(row=row, column=1, value=case.order)
            ws.cell(row=row, column=2, value=case.label)
            ws.cell(row=row, column=3, value=case.topic)
            ws.cell(row=row, column=4, value=case.supplied_treatment)
            ws.cell(row=row, column=5, value=", ".join(case.alternatives))
            treatment = ws.cell(row=row, column=6, value=case.supplied_treatment)
            rationale = ws.cell(row=row, column=7, value=case.model_rationale)
            consequence = ws.cell(row=row, column=8, value=case.model_consequence)
            wrap = Alignment(wrap_text=True, vertical="top")
            for cell in (treatment, rationale, consequence):
                cell.fill = PRACTICE_YELLOW
                cell.alignment = wrap
            dv = DataValidation(
                type="list",
                formula1='"' + ",".join(options) + '"',
                allow_blank=True,
            )
            ws.add_data_validation(dv)
            dv.add(treatment)

    def _build_normalization_judgment(self, wb: Workbook) -> None:
        ws = wb.create_sheet(NORMALIZATION_JUDGMENT_SHEET)
        ws["A1"] = "Normalization Judgment"
        ws["A1"].font = BOLD
        ws["A2"] = NORMALIZATION_JUDGMENT_INSTRUCTION
        ws["A3"] = NORMALIZATION_JUDGMENT_STEP_NOTE
        headers = [
            "Order",
            "Line item",
            "Scope",
            "Supplied reference treatment",
            "Alternative to evaluate",
            "Treatment to defend",
            "Rationale",
            "Economic consequence",
        ]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col, value=header)
            cell.font = BOLD
        widths = (8, 32, 36, 28, 32, 28, 40, 44)
        for idx, width in enumerate(widths, start=1):
            ws.column_dimensions[self._col(idx)].width = width

        for case in self.normalization_cases:
            row = 4 + case.order
            options = (case.reference_treatment,) + case.alternatives
            ws.cell(row=row, column=1, value=case.order)
            ws.cell(row=row, column=2, value=case.label)
            ws.cell(row=row, column=3, value=case.scope)
            ws.cell(row=row, column=4, value=case.reference_treatment)
            ws.cell(row=row, column=5, value=", ".join(case.alternatives))
            treatment = ws.cell(row=row, column=6, value=case.reference_treatment)
            rationale = ws.cell(row=row, column=7, value=case.model_rationale)
            consequence = ws.cell(row=row, column=8, value=case.model_consequence)
            wrap = Alignment(wrap_text=True, vertical="top")
            for cell in (treatment, rationale, consequence):
                cell.fill = PRACTICE_YELLOW
                cell.alignment = wrap
            dv = DataValidation(
                type="list",
                formula1='"' + ",".join(options) + '"',
                allow_blank=True,
            )
            ws.add_data_validation(dv)
            dv.add(treatment)

    def _build_earnings_normalization(self, wb: Workbook) -> None:
        from ..trainer.check_context import live_normalization_treatment_formula

        if self.normalization_series is None:
            raise RuntimeError("normalization_series required when building Earnings Normalization")

        ws = wb.create_sheet(EARNINGS_NORMALIZATION_SHEET)
        ws["A1"] = "Earnings Normalization"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Reported statements stay unchanged. Bridge reported NOPAT / Net Income to "
            "normalized earnings using the treatments chosen on Normalization Judgment."
        )
        ws.column_dimensions["A"].width = 40
        ws.column_dimensions["B"].width = 18

        header_row = 4
        ws.cell(row=header_row, column=1, value="Line item").font = BOLD
        ws.cell(row=header_row, column=2, value="Treatment").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=3 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(3 + j)].width = 14

        detail_start = header_row + 1
        for case in self.normalization_cases:
            row = header_row + case.order
            source_row = self.rowmap[f"Income Statement!{case.line_identity}"]
            ws.cell(row=row, column=1, value=case.label)
            formula = live_normalization_treatment_formula(
                4 + case.order,
                case.reference_treatment,
            )
            ws.cell(row=row, column=2, value=formula)
            for j in range(self._n):
                src_col = self._col(2 + j)
                cell = ws.cell(
                    row=row,
                    column=3 + j,
                    value=f"='Income Statement'!{src_col}{source_row}",
                )
                cell.number_format = NUM_FMT
        detail_end = header_row + len(self.normalization_cases)

        bridge_start = detail_end + 2
        nopat_r = self.rowmap["condensed_nopat_row"]
        ni_r = self.rowmap["condensed_ni_row"]
        etr_r = self.rowmap["condensed_etr_row"]
        series = self.normalization_series

        reported_nopat_row = bridge_start
        reported_ni_row = bridge_start + 1
        pretax_row = bridge_start + 2
        etr_row = bridge_start + 3
        after_tax_row = bridge_start + 4
        norm_nopat_row = bridge_start + 5
        norm_ni_row = bridge_start + 6
        check_row = bridge_start + 7

        bridge_labels = (
            (reported_nopat_row, "Reported NOPAT"),
            (reported_ni_row, "Reported Net Income"),
            (pretax_row, "Pretax Normalization Adjustment"),
            (etr_row, "Effective Tax Rate"),
            (after_tax_row, "After-tax Normalization Adjustment"),
            (norm_nopat_row, "Normalized NOPAT"),
            (norm_ni_row, "Normalized Net Income"),
            (check_row, "NORMALIZATION CHECK"),
        )
        for row, label in bridge_labels:
            font = BOLD if label in {"NORMALIZATION CHECK"} else None
            cell = ws.cell(row=row, column=1, value=label)
            if font is not None:
                cell.font = font

        treat_range = f"$B${detail_start}:$B${detail_end}"
        for j in range(self._n):
            period_col = self._col(3 + j)
            condensed_col = self._col(2 + j)
            value_range = f"{period_col}${detail_start}:{period_col}${detail_end}"

            reported_nopat = (
                f"='Condensed Financials'!{condensed_col}{nopat_r}"
            )
            reported_ni = f"='Condensed Financials'!{condensed_col}{ni_r}"
            pretax = f'=-SUMIF({treat_range},"Non-recurring",{value_range})'
            etr = f"='Condensed Financials'!{condensed_col}{etr_r}"
            after_tax = (
                f"=IF({period_col}{pretax_row}=0,0,"
                f"IF(ISNA({period_col}{etr_row}),NA(),"
                f"{period_col}{pretax_row}*(1-{period_col}{etr_row})))"
            )
            norm_nopat = f"={period_col}{reported_nopat_row}+{period_col}{after_tax_row}"
            norm_ni = f"={period_col}{reported_ni_row}+{period_col}{after_tax_row}"
            check = (
                f'=IF(AND(ABS(({period_col}{norm_nopat_row}-{period_col}{reported_nopat_row})'
                f"-{period_col}{after_tax_row})<0.01,"
                f"ABS(({period_col}{norm_ni_row}-{period_col}{reported_ni_row})"
                f"-{period_col}{after_tax_row})<0.01),\"OK\",\"CHECK\")"
            )

            for row, formula, fmt in (
                (reported_nopat_row, reported_nopat, NUM_FMT),
                (reported_ni_row, reported_ni, NUM_FMT),
                (pretax_row, pretax, NUM_FMT),
                (etr_row, etr, PCT_FMT),
                (after_tax_row, after_tax, NUM_FMT),
                (norm_nopat_row, norm_nopat, NUM_FMT),
                (norm_ni_row, norm_ni, NUM_FMT),
                (check_row, check, None),
            ):
                cell = ws.cell(row=row, column=3 + j, value=formula)
                if fmt is not None:
                    cell.number_format = fmt

            self._register_normalization(
                "pretax_normalization_adjustment",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                pretax_row,
                3 + j,
                pretax,
                series.pretax_adjustment[j],
            )
            self._register_normalization(
                "after_tax_normalization_adjustment",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                after_tax_row,
                3 + j,
                after_tax,
                series.after_tax_adjustment[j],
            )
            self._register_normalization(
                "normalized_nopat",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                norm_nopat_row,
                3 + j,
                norm_nopat,
                series.normalized_nopat[j],
            )
            self._register_normalization(
                "normalized_net_income",
                j,
                EARNINGS_NORMALIZATION_SHEET,
                norm_ni_row,
                3 + j,
                norm_ni,
                series.normalized_net_income[j],
            )

        self.rowmap["earnings_norm_detail_start"] = detail_start
        self.rowmap["earnings_norm_detail_end"] = detail_end
        self.rowmap["earnings_norm_pretax_row"] = pretax_row
        self.rowmap["earnings_norm_after_tax_row"] = after_tax_row
        self.rowmap["earnings_norm_nopat_row"] = norm_nopat_row
        self.rowmap["earnings_norm_ni_row"] = norm_ni_row
        self.rowmap["earnings_norm_check_row"] = check_row

    def _build_earnings_quality(self, wb: Workbook) -> None:
        if self.quality_series is None:
            raise RuntimeError("quality_series required when building Earnings Quality")

        ws = wb.create_sheet(EARNINGS_QUALITY_SHEET)
        ws["A1"] = f"{self.fin.company_name} — Earnings Quality"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Historical cash-conversion and accrual diagnostics. These are mechanical "
            "diagnostics, not an automatic quality score."
        )
        ws.column_dimensions["A"].width = 42

        header_row = 4
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        cfo_src = self._resolved_source_row(
            self.fin.cash_flow, "operating_cash_flow", required=True
        )
        assert cfo_src is not None
        ni_r = self.rowmap["condensed_ni_row"]
        series = self.quality_series

        cfo_row = 5
        ni_row = 6
        conversion_row = 7
        accruals_row = 8

        ws.cell(row=cfo_row, column=1, value="Operating Cash Flow")
        ws.cell(row=ni_row, column=1, value="Reported Net Income")
        ws.cell(row=conversion_row, column=1, value="Cash Conversion Ratio")
        ws.cell(row=accruals_row, column=1, value="Total Accruals (Net Income - CFO)")

        for j in range(self._n):
            col = self._col(2 + j)
            cfo_formula = f"='Cash Flow Statement'!{col}{cfo_src}"
            ni_formula = f"='Condensed Financials'!{col}{ni_r}"
            conversion_formula = (
                f"=IF({col}{ni_row}=0,NA(),{col}{cfo_row}/{col}{ni_row})"
            )
            accruals_formula = f"={col}{ni_row}-{col}{cfo_row}"

            c = ws.cell(row=cfo_row, column=2 + j, value=cfo_formula)
            c.number_format = NUM_FMT
            c = ws.cell(row=ni_row, column=2 + j, value=ni_formula)
            c.number_format = NUM_FMT
            c = ws.cell(row=conversion_row, column=2 + j, value=conversion_formula)
            c.number_format = "0.00x"
            c = ws.cell(row=accruals_row, column=2 + j, value=accruals_formula)
            c.number_format = NUM_FMT

            self._register_quality(
                "operating_cash_flow_link",
                j,
                EARNINGS_QUALITY_SHEET,
                cfo_row,
                2 + j,
                cfo_formula,
                series.operating_cash_flow[j],
            )
            self._register_quality(
                "cash_conversion_ratio",
                j,
                EARNINGS_QUALITY_SHEET,
                conversion_row,
                2 + j,
                conversion_formula,
                series.cash_conversion_ratio[j],
            )
            self._register_quality(
                "total_accruals",
                j,
                EARNINGS_QUALITY_SHEET,
                accruals_row,
                2 + j,
                accruals_formula,
                series.total_accruals[j],
            )

        self.rowmap["quality_cfo_row"] = cfo_row
        self.rowmap["quality_ni_row"] = ni_row
        self.rowmap["quality_conversion_row"] = conversion_row
        self.rowmap["quality_accruals_row"] = accruals_row

        if not self.quality_availability.total_assets:
            return

        assets_src = self._resolved_source_row(
            self.fin.balance_sheet, "total_assets", required=True
        )
        assert assets_src is not None
        assets_row = 10
        avg_assets_row = 11
        accrual_ratio_row = 12
        ws.cell(row=assets_row, column=1, value="Total Assets")
        ws.cell(row=avg_assets_row, column=1, value="Average Total Assets")
        ws.cell(row=accrual_ratio_row, column=1, value="Accrual Ratio")

        for j in range(self._n):
            col = self._col(2 + j)
            assets_formula = f"='Balance Sheet'!{col}{assets_src}"
            c = ws.cell(row=assets_row, column=2 + j, value=assets_formula)
            c.number_format = NUM_FMT

            if j == 0:
                ws.cell(row=avg_assets_row, column=2 + j, value=None)
                ws.cell(row=accrual_ratio_row, column=2 + j, value=None)
                continue

            prev_col = self._col(2 + j - 1)
            avg_formula = f"=({prev_col}{assets_row}+{col}{assets_row})/2"
            ratio_formula = (
                f"=IF({col}{avg_assets_row}=0,NA(),"
                f"{col}{accruals_row}/{col}{avg_assets_row})"
            )
            c = ws.cell(row=avg_assets_row, column=2 + j, value=avg_formula)
            c.number_format = NUM_FMT
            c = ws.cell(row=accrual_ratio_row, column=2 + j, value=ratio_formula)
            c.number_format = PCT_FMT

            assert series.average_total_assets[j] is not None
            assert series.accrual_ratio[j] is not None
            self._register_quality(
                "average_total_assets",
                j,
                EARNINGS_QUALITY_SHEET,
                avg_assets_row,
                2 + j,
                avg_formula,
                float(series.average_total_assets[j]),
            )
            accrual_expected = series.accrual_ratio[j]
            self._register_quality(
                "accrual_ratio",
                j,
                EARNINGS_QUALITY_SHEET,
                accrual_ratio_row,
                2 + j,
                ratio_formula,
                accrual_expected
                if isinstance(accrual_expected, str)
                else float(accrual_expected),
            )

        self.rowmap["quality_assets_row"] = assets_row
        self.rowmap["quality_avg_assets_row"] = avg_assets_row
        self.rowmap["quality_accrual_ratio_row"] = accrual_ratio_row

    def _build_working_capital_analysis(self, wb: Workbook) -> None:
        if self.working_capital_series is None:
            raise RuntimeError(
                "working_capital_series required when building Working Capital Analysis"
            )

        ws = wb.create_sheet(WORKING_CAPITAL_SHEET)
        ws["A1"] = "Working Capital Analysis"
        ws["A1"].font = BOLD
        ws["A2"] = (
            "Relate classified operating working capital to Revenue and identify how "
            "much incremental NOWC accompanies changes in sales."
        )
        ws["A3"] = (
            "These are diagnostics, not automatic judgments. Positive Change in NOWC "
            "is an operating cash use; negative Change in NOWC is a release. Annual "
            "data alone does not prove seasonality or deterioration."
        )
        ws.column_dimensions["A"].width = 48

        header_row = 5
        ws.cell(row=header_row, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            cell = ws.cell(row=header_row, column=2 + j, value=pd)
            cell.number_format = "mmm dd, yyyy"
            cell.font = BOLD
            ws.column_dimensions[self._col(2 + j)].width = 14

        rev_r = self.rowmap["condensed_revenue_row"]
        owca_r = self.rowmap["condensed_owca_row"]
        owcl_r = self.rowmap["condensed_owcl_row"]
        nowc_r = self.rowmap["condensed_nowc_row"]
        series = self.working_capital_series

        rev_row = 6
        owca_row = 7
        owcl_row = 8
        nowc_row = 9
        owca_ratio_row = 11
        owcl_ratio_row = 12
        nowc_ratio_row = 13
        rev_chg_row = 14
        nowc_chg_row = 15
        incr_row = 16

        ws.cell(row=rev_row, column=1, value="Revenue")
        ws.cell(row=owca_row, column=1, value="Operating Working Capital Assets")
        ws.cell(row=owcl_row, column=1, value="Operating Working Capital Liabilities")
        ws.cell(row=nowc_row, column=1, value="NOWC")
        ws.cell(row=owca_ratio_row, column=1, value="OWCA / Revenue")
        ws.cell(row=owcl_ratio_row, column=1, value="OWCL / Revenue")
        ws.cell(row=nowc_ratio_row, column=1, value="NOWC / Revenue")
        ws.cell(row=rev_chg_row, column=1, value="Change in Revenue")
        ws.cell(row=nowc_chg_row, column=1, value="Change in NOWC")
        ws.cell(row=incr_row, column=1, value="Incremental NOWC / Change in Revenue")

        for j in range(self._n):
            col = self._col(2 + j)
            for row, src in (
                (rev_row, rev_r),
                (owca_row, owca_r),
                (owcl_row, owcl_r),
                (nowc_row, nowc_r),
            ):
                formula = f"='Condensed Financials'!{col}{src}"
                c = ws.cell(row=row, column=2 + j, value=formula)
                c.number_format = NUM_FMT

            owca_ratio = f"=IF({col}{rev_row}=0,NA(),{col}{owca_row}/{col}{rev_row})"
            owcl_ratio = f"=IF({col}{rev_row}=0,NA(),{col}{owcl_row}/{col}{rev_row})"
            nowc_ratio = f"=IF({col}{rev_row}=0,NA(),{col}{nowc_row}/{col}{rev_row})"
            for row, formula in (
                (owca_ratio_row, owca_ratio),
                (owcl_ratio_row, owcl_ratio),
                (nowc_ratio_row, nowc_ratio),
            ):
                c = ws.cell(row=row, column=2 + j, value=formula)
                c.number_format = PCT_FMT

            self._register_working_capital(
                "owca_to_revenue",
                j,
                WORKING_CAPITAL_SHEET,
                owca_ratio_row,
                2 + j,
                owca_ratio,
                series.owca_to_revenue[j],
            )
            self._register_working_capital(
                "owcl_to_revenue",
                j,
                WORKING_CAPITAL_SHEET,
                owcl_ratio_row,
                2 + j,
                owcl_ratio,
                series.owcl_to_revenue[j],
            )
            self._register_working_capital(
                "nowc_to_revenue",
                j,
                WORKING_CAPITAL_SHEET,
                nowc_ratio_row,
                2 + j,
                nowc_ratio,
                series.nowc_to_revenue[j],
            )

            if j == 0:
                ws.cell(row=rev_chg_row, column=2 + j, value="N/A")
                ws.cell(row=nowc_chg_row, column=2 + j, value="N/A")
                ws.cell(row=incr_row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            rev_chg = f"={col}{rev_row}-{prev_col}{rev_row}"
            nowc_chg = f"={col}{nowc_row}-{prev_col}{nowc_row}"
            incr = (
                f"=IF({col}{rev_chg_row}=0,NA(),"
                f"{col}{nowc_chg_row}/{col}{rev_chg_row})"
            )
            c = ws.cell(row=rev_chg_row, column=2 + j, value=rev_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=nowc_chg_row, column=2 + j, value=nowc_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=incr_row, column=2 + j, value=incr)
            c.number_format = PCT_FMT

            assert series.revenue_change[j] is not None
            assert series.nowc_change[j] is not None
            assert series.incremental_nowc_to_revenue_change[j] is not None
            self._register_working_capital(
                "revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                rev_chg_row,
                2 + j,
                rev_chg,
                float(series.revenue_change[j]),
            )
            self._register_working_capital(
                "nowc_change",
                j,
                WORKING_CAPITAL_SHEET,
                nowc_chg_row,
                2 + j,
                nowc_chg,
                float(series.nowc_change[j]),
            )
            incr_expected = series.incremental_nowc_to_revenue_change[j]
            self._register_working_capital(
                "incremental_nowc_to_revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                incr_row,
                2 + j,
                incr,
                incr_expected
                if isinstance(incr_expected, str)
                else float(incr_expected),
            )

        # Driver decomposition section (Step 9B.2)
        section_row = 18
        owca_change_row = 19
        owcl_change_row = 20
        nowc_bridge_row = 21
        incremental_owca_row = 22
        incremental_owcl_row = 23
        driver_check_row = 24

        ws.cell(row=section_row, column=1, value="WORKING-CAPITAL DRIVER DECOMPOSITION").font = BOLD
        ws.cell(row=owca_change_row, column=1, value="Change in OWCA")
        ws.cell(row=owcl_change_row, column=1, value="Change in OWCL")
        ws.cell(row=nowc_bridge_row, column=1, value="Change in NOWC from Components")
        ws.cell(
            row=incremental_owca_row,
            column=1,
            value="Incremental OWCA / Change in Revenue",
        )
        ws.cell(
            row=incremental_owcl_row,
            column=1,
            value="Incremental OWCL / Change in Revenue",
        )
        ws.cell(row=driver_check_row, column=1, value="DRIVER DECOMPOSITION CHECK").font = BOLD

        for j in range(self._n):
            col = self._col(2 + j)
            if j == 0:
                for row in (
                    owca_change_row,
                    owcl_change_row,
                    nowc_bridge_row,
                    incremental_owca_row,
                    incremental_owcl_row,
                    driver_check_row,
                ):
                    ws.cell(row=row, column=2 + j, value="N/A")
                continue

            prev_col = self._col(2 + j - 1)
            owca_chg = f"={col}{owca_row}-{prev_col}{owca_row}"
            owcl_chg = f"={col}{owcl_row}-{prev_col}{owcl_row}"
            nowc_bridge = f"={col}{owca_change_row}-{col}{owcl_change_row}"
            incr_owca = (
                f"=IF({col}{rev_chg_row}=0,NA(),"
                f"{col}{owca_change_row}/{col}{rev_chg_row})"
            )
            incr_owcl = (
                f"=IF({col}{rev_chg_row}=0,NA(),"
                f"{col}{owcl_change_row}/{col}{rev_chg_row})"
            )
            driver_check = (
                f'=IF(ABS({col}{nowc_bridge_row}-{col}{nowc_chg_row})<0.01,'
                f'"OK","CHECK")'
            )

            c = ws.cell(row=owca_change_row, column=2 + j, value=owca_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=owcl_change_row, column=2 + j, value=owcl_chg)
            c.number_format = NUM_FMT
            c = ws.cell(row=nowc_bridge_row, column=2 + j, value=nowc_bridge)
            c.number_format = NUM_FMT
            c = ws.cell(row=incremental_owca_row, column=2 + j, value=incr_owca)
            c.number_format = PCT_FMT
            c = ws.cell(row=incremental_owcl_row, column=2 + j, value=incr_owcl)
            c.number_format = PCT_FMT
            ws.cell(row=driver_check_row, column=2 + j, value=driver_check)

            assert series.owca_change[j] is not None
            assert series.owcl_change[j] is not None
            assert series.nowc_change_from_components[j] is not None
            self._register_working_capital(
                "owca_change",
                j,
                WORKING_CAPITAL_SHEET,
                owca_change_row,
                2 + j,
                owca_chg,
                float(series.owca_change[j]),
            )
            self._register_working_capital(
                "owcl_change",
                j,
                WORKING_CAPITAL_SHEET,
                owcl_change_row,
                2 + j,
                owcl_chg,
                float(series.owcl_change[j]),
            )
            self._register_working_capital(
                "nowc_change_from_components",
                j,
                WORKING_CAPITAL_SHEET,
                nowc_bridge_row,
                2 + j,
                nowc_bridge,
                float(series.nowc_change_from_components[j]),
            )
            incr_owca_expected = series.incremental_owca_to_revenue_change[j]
            assert incr_owca_expected is not None
            self._register_working_capital(
                "incremental_owca_to_revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                incremental_owca_row,
                2 + j,
                incr_owca,
                incr_owca_expected
                if isinstance(incr_owca_expected, str)
                else float(incr_owca_expected),
            )
            incr_owcl_expected = series.incremental_owcl_to_revenue_change[j]
            assert incr_owcl_expected is not None
            self._register_working_capital(
                "incremental_owcl_to_revenue_change",
                j,
                WORKING_CAPITAL_SHEET,
                incremental_owcl_row,
                2 + j,
                incr_owcl,
                incr_owcl_expected
                if isinstance(incr_owcl_expected, str)
                else float(incr_owcl_expected),
            )

        self.rowmap["wc_revenue_row"] = rev_row
        self.rowmap["wc_owca_row"] = owca_row
        self.rowmap["wc_owcl_row"] = owcl_row
        self.rowmap["wc_nowc_row"] = nowc_row
        self.rowmap["wc_owca_change_row"] = owca_change_row
        self.rowmap["wc_owcl_change_row"] = owcl_change_row
        self.rowmap["wc_nowc_bridge_row"] = nowc_bridge_row
        self.rowmap["wc_incremental_owca_row"] = incremental_owca_row
        self.rowmap["wc_incremental_owcl_row"] = incremental_owcl_row
        self.rowmap["wc_driver_check_row"] = driver_check_row

    def _build_model_tab(self, wb: Workbook, scenario: str) -> None:
        ws = wb.create_sheet(f"Model_{scenario}")
        sc = self.assumptions["scenarios"][scenario]
        result = self._scenario_results[scenario]
        ws["A1"] = f"{self.fin.company_name} — {scenario} Scenario"
        ws.freeze_panes = "B1"
        ws.column_dimensions["A"].width = 42

        ws["A5"] = "Cost of Equity (Ke)"
        ws["B5"] = sc["costOfEquity"]
        ws["B5"].font = BLUE
        ws["B5"].number_format = PCT_FMT
        ws["A6"] = "Tax rate"
        ws["B6"] = sc.get("taxRate", 0.165)
        ws["B6"].number_format = PCT_FMT
        # Historical average is already after-tax — use directly; do not tax again.
        ws["A7"] = "After-tax CoD"
        ws["B7"] = self.anchor.hist_avg_after_tax_cod
        ws["B7"].number_format = PCT_FMT
        ws["A8"] = "Financial leverage"
        ws["B8"] = self.anchor.leverage
        ws["B8"].number_format = PCT_FMT
        ws["A9"] = "Terminal growth (g)"
        ws["B9"] = sc["terminalGrowth"]
        ws["B9"].font = BLUE
        ws["B9"].number_format = PCT_FMT

        fc = self._first_fc_col
        anchor_col = self._col(self._last_fy_col)
        rev_row = self._resolved_source_row(
            self.fin.income_statement, "revenue", required=True
        )
        nowc_hist = self.rowmap["condensed_nowc_row"]
        noa_hist = self.rowmap["condensed_noa_row"]
        nd_hist = self.rowmap["condensed_nd_row"]
        # NOLA_hist = NOA - NOWC for Y1 bridge
        nola_hist_formula = (
            f"='Condensed Financials'!{anchor_col}{noa_hist}"
            f"-'Condensed Financials'!{anchor_col}{nowc_hist}"
        )

        sales_row, margin_row = 21, 22
        nowc_row, nola_row, nd_row, eq_row = 23, 24, 25, 26
        nopat_row, ni_row, ae_row = 27, 28, 29
        disc_row, pv_ae_row = 30, 31
        sum_pv_ae_row, tv_row, tv_pv_row = 35, 36, 37
        iv_row, shares_row, ivps_row = 38, 39, 40

        ws.cell(row=20, column=1, value="FORECAST BLOCK").font = BOLD
        for t in range(10):
            ws.cell(row=20, column=fc + t, value=f"Y{t + 1}").font = BOLD
            ws.column_dimensions[self._col(fc + t)].width = 14

        labels = {
            sales_row: "Sales",
            margin_row: "NOPAT Margin",
            nowc_row: "NOWC",
            nola_row: "NOLA",
            nd_row: "Net Debt",
            eq_row: "Book Equity",
            nopat_row: "NOPAT",
            ni_row: "Net Income",
            ae_row: "Abnormal Earnings",
            disc_row: "Discount Factor",
            pv_ae_row: "PV Abnormal Earnings",
        }
        for row, label in labels.items():
            ws.cell(row=row, column=1, value=label)

        ws.cell(row=sum_pv_ae_row, column=1, value="Sum PV Abnormal Earnings")
        ws.cell(row=tv_row, column=1, value="Terminal Value")
        ws.cell(row=tv_pv_row, column=1, value="PV Terminal Value")
        ws.cell(row=iv_row, column=1, value="Intrinsic Value")
        ws.cell(row=shares_row, column=1, value="Diluted Shares")
        ws.cell(row=ivps_row, column=1, value="Intrinsic Value per Share")

        for t in range(10):
            col_i = fc + t
            col = self._col(col_i)
            prev = self._col(col_i - 1) if t > 0 else None
            g = sc["growthVector"][t]
            m = sc["marginVector"][t]
            nowc_ratio = sc["nowcRatioVector"][t]
            nola_ratio = sc["nolaRatioVector"][t]

            if t == 0:
                sales_f = f"='Income Statement'!{anchor_col}{rev_row}*(1+{g})"
            else:
                sales_f = f"={prev}{sales_row}*(1+{g})"
            ws.cell(row=sales_row, column=col_i, value=sales_f).number_format = NUM_FMT

            mc = ws.cell(row=margin_row, column=col_i, value=m)
            mc.font = BLUE
            mc.number_format = PCT_FMT

            if t == 0:
                ws.cell(
                    row=nowc_row,
                    column=col_i,
                    value=f"='Condensed Financials'!{anchor_col}{nowc_hist}",
                ).number_format = NUM_FMT
                ws.cell(row=nola_row, column=col_i, value=nola_hist_formula).number_format = NUM_FMT
                ws.cell(
                    row=nd_row,
                    column=col_i,
                    value=f"='Condensed Financials'!{anchor_col}{nd_hist}",
                ).number_format = NUM_FMT
            else:
                ws.cell(
                    row=nowc_row,
                    column=col_i,
                    value=f"={col}{sales_row}*{nowc_ratio}",
                ).number_format = NUM_FMT
                ws.cell(
                    row=nola_row,
                    column=col_i,
                    value=f"={col}{sales_row}*{nola_ratio}",
                ).number_format = NUM_FMT
                ws.cell(
                    row=nd_row,
                    column=col_i,
                    value=f"=($B$8)*({col}{nowc_row}+{col}{nola_row})",
                ).number_format = NUM_FMT

            ws.cell(
                row=eq_row,
                column=col_i,
                value=f"={col}{nowc_row}+{col}{nola_row}-{col}{nd_row}",
            ).number_format = NUM_FMT
            ws.cell(
                row=nopat_row,
                column=col_i,
                value=f"={col}{sales_row}*{col}{margin_row}",
            ).number_format = NUM_FMT
            if scenario == "Base" and t == 0:
                ws.cell(row=nopat_row, column=col_i).fill = GREEN

            # After-tax CoD in B7 already after-tax — apply once.
            ws.cell(
                row=ni_row,
                column=col_i,
                value=f"={col}{nopat_row}-{col}{nd_row}*$B$7",
            ).number_format = NUM_FMT
            ws.cell(
                row=ae_row,
                column=col_i,
                value=f"={col}{ni_row}-$B$5*{col}{eq_row}",
            ).number_format = NUM_FMT
            if scenario == "Base" and t == 0:
                ws.cell(row=ae_row, column=col_i).fill = GREEN

            ws.cell(
                row=disc_row,
                column=col_i,
                value=f"=1/(1+$B$5)^{t + 1}",
            ).number_format = "0.0000"
            ws.cell(
                row=pv_ae_row,
                column=col_i,
                value=f"={col}{ae_row}*{col}{disc_row}",
            ).number_format = NUM_FMT

        last_fc = self._col(fc + 9)
        first_fc = self._col(fc)
        sum_pv = f"=SUM({first_fc}{pv_ae_row}:{last_fc}{pv_ae_row})"
        ws.cell(row=sum_pv_ae_row, column=fc, value=sum_pv).number_format = NUM_FMT

        tv_formula = f"={last_fc}{ae_row}*(1+$B$9)/($B$5-$B$9)"
        ws.cell(row=tv_row, column=fc + 9, value=tv_formula).number_format = NUM_FMT

        tv_pv_formula = f"={last_fc}{tv_row}*{last_fc}{disc_row}"
        ws.cell(row=tv_pv_row, column=fc, value=tv_pv_formula).number_format = NUM_FMT

        iv_formula = f"={first_fc}{eq_row}+{first_fc}{sum_pv_ae_row}+{first_fc}{tv_pv_row}"
        ws.cell(row=iv_row, column=fc, value=iv_formula).number_format = NUM_FMT

        shares_cell = ws.cell(
            row=shares_row,
            column=fc,
            value=self.assumptions["marketData"]["dilutedShares"],
        )
        shares_cell.font = BLUE
        shares_cell.number_format = NUM_FMT

        ivps_formula = f"={first_fc}{iv_row}/{first_fc}{shares_row}"
        ivps_cell = ws.cell(row=ivps_row, column=fc, value=ivps_formula)
        ivps_cell.number_format = "0.0000"
        if scenario == "Base":
            ivps_cell.fill = GREEN

        self.rowmap[f"model_{scenario}_ivps_row"] = ivps_row
        self.rowmap[f"model_{scenario}_fc_col"] = fc
        self.rowmap[f"model_{scenario}_ae_row"] = ae_row
        self.rowmap[f"model_{scenario}_disc_row"] = disc_row
        self.rowmap[f"model_{scenario}_tv_row"] = tv_row
        self.rowmap[f"model_{scenario}_sales_row"] = sales_row

        if scenario == "Base":
            sales_y1 = str(ws.cell(row=sales_row, column=fc).value)
            nopat_y1 = str(ws.cell(row=nopat_row, column=fc).value)
            ae_y1 = str(ws.cell(row=ae_row, column=fc).value)
            self._register_deferred(
                "model_sales_y1",
                f"Model_{scenario}",
                sales_row,
                fc,
                sales_y1,
                result.sales_y1,
            )
            self._register_deferred(
                "model_nopat_y1",
                f"Model_{scenario}",
                nopat_row,
                fc,
                nopat_y1,
                result.nopat_y1,
            )
            self._register_deferred(
                "model_ae_y1",
                f"Model_{scenario}",
                ae_row,
                fc,
                ae_y1,
                result.abnormal_earnings_y1,
            )
            self._register_deferred(
                "model_tv",
                f"Model_{scenario}",
                tv_pv_row,
                fc,
                tv_pv_formula,
                result.terminal_value_pv,
            )
            self._register_deferred(
                "model_ivps",
                f"Model_{scenario}",
                ivps_row,
                fc,
                ivps_formula,
                result.ivps,
            )

    def _build_scenario_summary(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Scenario_Summary")
        ws["A1"] = f"{self.fin.company_name} — Scenario Summary"
        for j, h in enumerate(["Scenario", "Probability", "IVPS"], start=1):
            ws.cell(row=3, column=j, value=h).font = BOLD
        for i, name in enumerate(("Bear", "Base", "Bull"), start=4):
            sc = self.assumptions["scenarios"][name]
            ivps_row = self.rowmap[f"model_{name}_ivps_row"]
            fc = self.rowmap[f"model_{name}_fc_col"]
            ws.cell(row=i, column=1, value=name)
            ws.cell(row=i, column=2, value=sc["probability"])
            ws.cell(row=i, column=2).font = BLUE
            ws.cell(row=i, column=2).number_format = PCT_FMT
            ws.cell(row=i, column=3, value=f"='Model_{name}'!{self._col(fc)}{ivps_row}")
        weighted_row = 8
        weighted_col = 5
        weighted_formula = "=SUMPRODUCT(B4:B6,C4:C6)"
        ws.cell(row=weighted_row, column=1, value="Weighted IVPS")
        ws.cell(row=weighted_row, column=weighted_col, value=weighted_formula)
        ws.cell(row=weighted_row, column=weighted_col).fill = GREEN
        w_ivps = weighted_ivps(self._scenario_results, self.assumptions["scenarios"])
        self._register_deferred(
            "scenario_weighted",
            "Scenario_Summary",
            weighted_row,
            weighted_col,
            weighted_formula,
            w_ivps,
        )
