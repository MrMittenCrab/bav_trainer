"""Build the complete reference BAV workbook and semantic component map."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from ..data.interface import LineItem, StandardizedFinancials
from ..data.schema import normalize_label
from ..model.financial_math import compute_anchor, guess_classification
from ..model.ri_engine import run_scenario, weighted_ivps
from .component_catalog import catalog_by_id, COMPONENT_CATALOG
from .map_embed import embed_component_map_sheet
from .semantic_map import SemanticMap

NUM_FMT = "#,##0;(#,##0)"
PCT_FMT = "0.0%"
BLUE = Font(color="0000FF")
BOLD = Font(bold=True)
ORANGE = PatternFill("solid", start_color="FCE5CD")
YELLOW = PatternFill("solid", start_color="FFF2CC")
GREEN = PatternFill("solid", start_color="D9EAD3")

CLASSIFICATIONS = [
    "Operating Working Capital Asset",
    "Operating Working Capital Liability",
    "Operating Long-Term Asset",
    "Operating Long-Term Liability",
    "Financial Asset",
    "Financial Liability",
    "Ambiguous — Operating",
    "Ambiguous — Financial",
]


class ReferenceModelBuilder:
    """Construct reference workbook and populate SemanticMap at build time."""

    def __init__(
        self,
        financials: StandardizedFinancials,
        assumptions: dict[str, Any] | None = None,
    ):
        self.fin = financials
        self.periods = financials.fiscal_years() or financials.period_dates()
        self.assumptions = assumptions or self._default_assumptions()
        self.rowmap: dict[str, Any] = {}
        self.semantic_map = SemanticMap()
        self.anchor = compute_anchor(financials, self.periods)
        self._n = len(self.periods)
        self._last_fy_col = 2 + self._n - 1
        self._first_fc_col = 2 + self._n
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
            rev_item = self.fin.income_statement[0]
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
            "meta": {"anchorRevenue": anchor_rev, "currency": self.fin.units},
        }

    def build(self, output_path: Path) -> SemanticMap:
        wb = Workbook()
        self._build_source_tabs(wb)
        self._build_condensed(wb)
        self._build_dupont(wb)
        for scenario in ("Bear", "Base", "Bull"):
            self._build_model_tab(wb, scenario)
        self._build_scenario_summary(wb)

        errors = self.semantic_map.validate_complete()
        if errors:
            raise ValueError("Component map validation failed:\n" + "\n".join(errors))

        embed_component_map_sheet(wb, self.semantic_map)
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

    def _register(
        self,
        spec_id: str,
        tab: str,
        row: int,
        col: int,
        formula: str,
        expected: float | str,
        related: list[str] | None = None,
    ) -> None:
        spec = catalog_by_id()[spec_id]
        self.semantic_map.register(spec, tab, row, col, formula, expected, related_cells=related)

    def _find_row(self, label_fragment: str) -> int | None:
        for key, row in self.rowmap.items():
            if isinstance(row, int) and label_fragment.lower() in key.lower():
                return row
        return None

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
        for item in items:
            ws.cell(row=r, column=1, value=item.label)
            for j, pd in enumerate(self.periods):
                val = item.values.get(pd)
                c = ws.cell(row=r, column=2 + j, value=val)
                c.number_format = NUM_FMT
            self.rowmap[normalize_label(item.label)] = r
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
        r = 4
        ws.cell(row=r, column=1, value="BALANCE SHEET CLASSIFICATION").font = BOLD
        r += 1
        class_start = r
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(CLASSIFICATIONS)}"',
            allow_blank=True,
        )
        ws.add_data_validation(dv)
        for item in self.fin.balance_sheet:
            if "total" in item.label.lower():
                continue
            ws.cell(row=r, column=1, value=item.label)
            cat = guess_classification(item.label)
            ws.cell(row=r, column=2, value=cat)
            if cat:
                dv.add(ws.cell(row=r, column=2))
            r += 1
        class_end = r - 1

        r += 1
        ws.cell(row=r, column=1, value="CONDENSED INCOME STATEMENT").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        r += 1

        ni_row = self._find_row("profit") or self._find_row("net income")
        pretax_row = self._find_row("pretax") or self._find_row("before tax")
        tax_row = self._find_row("tax")
        row_nums: dict[str, int] = {}

        for label, src_row, bold in [
            ("Net Income", ni_row, False),
            ("Pretax Income", pretax_row, False),
            ("Tax Expense", tax_row, False),
        ]:
            if not src_row:
                continue
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            for j in range(self._n):
                col = self._col(2 + j)
                ws.cell(row=r, column=2 + j, value=f"='Income Statement'!{col}{src_row}")
            row_nums[label] = r
            r += 1

        ws.cell(row=r, column=1, value="Effective Tax Rate")
        for j in range(self._n):
            col = self._col(2 + j)
            if "Tax Expense" in row_nums and "Pretax Income" in row_nums:
                ws.cell(
                    row=r,
                    column=2 + j,
                    value=f"=-{col}{row_nums['Tax Expense']}/{col}{row_nums['Pretax Income']}",
                ).number_format = PCT_FMT
        r += 1

        nopat_row = r
        ws.cell(row=r, column=1, value="NOPAT").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            if "Net Income" in row_nums:
                c = ws.cell(row=r, column=2 + j, value=f"={col}{row_nums['Net Income']}")
                c.fill = GREEN
        r += 1
        self.rowmap["condensed_nopat_row"] = nopat_row

        lc = self._last_fy_col
        nopat_formula = ws.cell(row=nopat_row, column=lc).value
        self._register(
            "nopat_fy",
            "Condensed Financials",
            nopat_row,
            lc,
            str(nopat_formula),
            self.anchor.nopat,
        )

        r += 1
        ws.cell(row=r, column=1, value="CONDENSED BALANCE SHEET").font = BOLD
        r += 1

        nowc_row = r
        ws.cell(row=r, column=1, value="NOWC").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            f = (
                f'=SUMIF($B${class_start}:$B${class_end},"Operating Working Capital Asset",'
                f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                f'-SUMIF($B${class_start}:$B${class_end},"Operating Working Capital Liability",'
                f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
            )
            ws.cell(row=r, column=2 + j, value=f)
        r += 1
        self._register(
            "nowc_agg",
            "Condensed Financials",
            nowc_row,
            lc,
            str(ws.cell(row=nowc_row, column=lc).value),
            self.anchor.nowc,
        )

        noa_row = r
        ws.cell(row=r, column=1, value="NOA").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            f = (
                f"={col}{nowc_row}+"
                f'SUMIF($B${class_start}:$B${class_end},"Operating Long-Term Asset",'
                f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                f'-SUMIF($B${class_start}:$B${class_end},"Operating Long-Term Liability",'
                f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
            )
            ws.cell(row=r, column=2 + j, value=f)
        r += 1
        self._register(
            "noa_agg",
            "Condensed Financials",
            noa_row,
            lc,
            str(ws.cell(row=noa_row, column=lc).value),
            self.anchor.noa,
        )

        nd_row = r
        ws.cell(row=r, column=1, value="Net Debt").font = BOLD
        for j in range(self._n):
            col = self._col(2 + j)
            f = (
                f'=SUMIF($B${class_start}:$B${class_end},"Financial Liability",'
                f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                f'-SUMIF($B${class_start}:$B${class_end},"Financial Asset",'
                f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
            )
            ws.cell(row=r, column=2 + j, value=f)
        self._register(
            "net_debt",
            "Condensed Financials",
            nd_row,
            lc,
            str(ws.cell(row=nd_row, column=lc).value),
            self.anchor.net_debt,
        )

    def _build_dupont(self, wb: Workbook) -> None:
        ws = wb.create_sheet("ALT DuPont")
        ws["A1"] = f"{self.fin.company_name} — DuPont Decomposition"
        ws["A2"] = "ROE = RNOA + FLEV × Spread"
        ws.column_dimensions["A"].width = 42
        r_hdr = 4
        ws.cell(row=r_hdr, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            if j == 0:
                continue
            c = ws.cell(row=r_hdr, column=1 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD

        nopat_r = self.rowmap.get("condensed_nopat_row")
        ni_row = self._find_row("profit") or self._find_row("net income")
        noa_r = None
        nd_r = None
        for key, val in self.semantic_map.rowmap.items():
            if key == "condensed.noa.latest_fy":
                noa_r = val["row"]
            if key == "condensed.net_debt.latest_fy":
                nd_r = val["row"]

        metrics = ["RNOA", "After-tax CoD", "Spread", "FLEV", "ROE (decomposed)", "Actual ROE"]
        metric_rows: dict[str, int] = {}
        r = r_hdr + 1
        for metric in metrics:
            ws.cell(row=r, column=1, value=metric)
            metric_rows[metric] = r
            r += 1

        j_last = self._n - 1
        col = self._col(1 + j_last)
        prev = self._col(1 + j_last - 1)
        rnoa_row = metric_rows["RNOA"]
        ws.cell(
            row=rnoa_row,
            column=1 + j_last,
            value=(
                f"='Condensed Financials'!{col}{nopat_r}/"
                f"(('Condensed Financials'!{col}{noa_r}+'Condensed Financials'!{prev}{noa_r})/2)"
            ),
        ).fill = YELLOW

        cod_row = metric_rows["After-tax CoD"]
        ws.cell(
            row=cod_row,
            column=1 + j_last,
            value=f"='Condensed Financials'!{col}{nopat_r}/('Condensed Financials'!{col}{nd_r})",
        )

        spread_row = metric_rows["Spread"]
        ws.cell(
            row=spread_row,
            column=1 + j_last,
            value=f"={col}{rnoa_row}-{col}{cod_row}",
        )

        flev_row = metric_rows["FLEV"]
        ws.cell(
            row=flev_row,
            column=1 + j_last,
            value=(
                f"=('Condensed Financials'!{col}{nd_r}+'Condensed Financials'!{prev}{nd_r})/2/"
                f"(('Balance Sheet'!{col}7+'Balance Sheet'!{prev}7)/2)"
            ),
        )

        roe_row = metric_rows["ROE (decomposed)"]
        ws.cell(
            row=roe_row,
            column=1 + j_last,
            value=f"={col}{rnoa_row}+{col}{flev_row}*({col}{spread_row})",
        ).fill = YELLOW

        actual_row = metric_rows["Actual ROE"]
        ws.cell(
            row=actual_row,
            column=1 + j_last,
            value=f"='Income Statement'!{col}{ni_row}/(('Balance Sheet'!{col}7+'Balance Sheet'!{prev}7)/2)",
        )

        dup = self.anchor.dupont
        self._register(
            "rnoa",
            "ALT DuPont",
            rnoa_row,
            1 + j_last,
            str(ws.cell(row=rnoa_row, column=1 + j_last).value),
            dup["RNOA"][j_last],
        )
        self._register(
            "spread",
            "ALT DuPont",
            spread_row,
            1 + j_last,
            str(ws.cell(row=spread_row, column=1 + j_last).value),
            dup["Spread"][j_last],
        )
        self._register(
            "roe_decomp",
            "ALT DuPont",
            roe_row,
            1 + j_last,
            str(ws.cell(row=roe_row, column=1 + j_last).value),
            dup["ROE (decomposed)"][j_last],
        )

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
        ws["A7"] = "After-tax CoD"
        ws["B7"] = self.anchor.hist_avg_after_tax_cod
        ws["B7"].number_format = PCT_FMT
        ws["A8"] = "After-tax CoD (model)"
        ws["B8"] = f"=B7*(1-B6)"
        ws["B8"].number_format = PCT_FMT
        ws["A9"] = "Terminal growth (g)"
        ws["B9"] = sc["terminalGrowth"]
        ws["B9"].font = BLUE
        ws["B9"].number_format = PCT_FMT

        fc = self._first_fc_col
        fc_col = self._col(fc)
        anchor_col = self._col(self._last_fy_col)
        rev_row = self._find_row("revenue") or self._find_row("turnover") or 7

        sales_row, margin_row, nopat_row = 31, 32, 34
        ae_row, pv_ae_row, tv_pv_row, iv_row, shares_row, ivps_row = 42, 45, 47, 49, 50, 51

        ws.cell(row=30, column=1, value="FORECAST BLOCK").font = BOLD
        ws.cell(row=sales_row, column=1, value="Sales")
        ws.cell(row=margin_row, column=1, value="NOPAT Margin")
        ws.cell(row=nopat_row, column=1, value="NOPAT")
        ws.cell(row=41, column=1, value="Abnormal Earnings")
        ws.cell(row=ae_row, column=1, value="Abnormal Earnings (Y1)")
        ws.cell(row=pv_ae_row, column=1, value="PV Abnormal Earnings")
        ws.cell(row=tv_pv_row, column=1, value="PV Terminal Value")
        ws.cell(row=48, column=1, value="Book Equity (Y1)")
        ws.cell(row=iv_row, column=1, value="Intrinsic Value")
        ws.cell(row=shares_row, column=1, value="Diluted Shares")
        ws.cell(row=ivps_row, column=1, value="Intrinsic Value per Share")

        sales_formula = f"='Income Statement'!{anchor_col}{rev_row}*(1+{sc['growthVector'][0]})"
        ws.cell(row=sales_row, column=fc, value=sales_formula)
        ws.cell(row=margin_row, column=fc, value=sc["marginVector"][0])
        ws.cell(row=margin_row, column=fc).font = BLUE
        ws.cell(row=margin_row, column=fc).number_format = PCT_FMT
        nopat_formula = f"={fc_col}{sales_row}*{fc_col}{margin_row}"
        ws.cell(row=nopat_row, column=fc, value=nopat_formula)
        if scenario == "Base":
            ws.cell(row=nopat_row, column=fc).fill = GREEN

        # Simplified AE chain for Y1
        eq_formula = f"='Condensed Financials'!{anchor_col}{self.semantic_map.rowmap['condensed.noa.latest_fy']['row']}-'Condensed Financials'!{anchor_col}{self.semantic_map.rowmap['condensed.net_debt.latest_fy']['row']}"
        ws.cell(row=48, column=fc, value=eq_formula)
        ni_formula = f"={fc_col}{nopat_row}-'Condensed Financials'!{anchor_col}{self.semantic_map.rowmap['condensed.net_debt.latest_fy']['row']}*B8"
        ws.cell(row=40, column=fc, value=ni_formula)
        ae_formula = f"={fc_col}40-B5*{fc_col}48"
        ws.cell(row=ae_row, column=fc, value=ae_formula)
        if scenario == "Base":
            ws.cell(row=ae_row, column=fc).fill = GREEN

        pv_factor = f"=1/(1+B5)"
        ws.cell(row=44, column=fc, value=pv_factor)
        pv_ae_formula = f"={fc_col}{ae_row}*{fc_col}44"
        ws.cell(row=pv_ae_row, column=fc, value=pv_ae_formula)

        last_fc = self._col(self._first_fc_col + 9)
        tv_formula = f"={last_fc}{ae_row}*(1+B9)/(B5-B9)"
        ws.cell(row=46, column=self._first_fc_col + 9, value=tv_formula)
        tv_pv_formula = f"={last_fc}46*{last_fc}44"
        ws.cell(row=tv_pv_row, column=fc, value=tv_pv_formula)

        iv_formula = f"={fc_col}48+{fc_col}{pv_ae_row}+{fc_col}{tv_pv_row}"
        ws.cell(row=iv_row, column=fc, value=iv_formula)
        ws.cell(row=shares_row, column=fc, value=self.assumptions["marketData"]["dilutedShares"])
        ws.cell(row=shares_row, column=fc).font = BLUE
        ivps_formula = f"={fc_col}{iv_row}/{fc_col}{shares_row}"
        ws.cell(row=ivps_row, column=fc, value=ivps_formula)
        if scenario == "Base":
            ws.cell(row=ivps_row, column=fc).fill = GREEN

        if scenario == "Base":
            self._register(
                "model_sales_y1",
                f"Model_{scenario}",
                sales_row,
                fc,
                sales_formula,
                result.sales_y1,
            )
            self._register(
                "model_nopat_y1",
                f"Model_{scenario}",
                nopat_row,
                fc,
                nopat_formula,
                result.nopat_y1,
            )
            self._register(
                "model_ae_y1",
                f"Model_{scenario}",
                ae_row,
                fc,
                ae_formula,
                result.abnormal_earnings_y1,
            )
            self._register(
                "model_tv",
                f"Model_{scenario}",
                tv_pv_row,
                fc,
                tv_pv_formula,
                result.terminal_value_pv,
            )
            self._register(
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
        base_ivps_row = 51
        base_fc = self._first_fc_col
        for i, name in enumerate(("Bear", "Base", "Bull"), start=4):
            sc = self.assumptions["scenarios"][name]
            ws.cell(row=i, column=1, value=name)
            ws.cell(row=i, column=2, value=sc["probability"])
            ws.cell(row=i, column=2).font = BLUE
            ws.cell(row=i, column=2).number_format = PCT_FMT
            ws.cell(row=i, column=3, value=f"='Model_{name}'!{self._col(base_fc)}{base_ivps_row}")
        weighted_row = 8
        weighted_col = 5
        weighted_formula = "=SUMPRODUCT(B4:B6,C4:C6)"
        ws.cell(row=weighted_row, column=1, value="Weighted IVPS")
        ws.cell(row=weighted_row, column=weighted_col, value=weighted_formula)
        ws.cell(row=weighted_row, column=weighted_col).fill = GREEN
        w_ivps = weighted_ivps(self._scenario_results, self.assumptions["scenarios"])
        self._register(
            "scenario_weighted",
            "Scenario_Summary",
            weighted_row,
            weighted_col,
            weighted_formula,
            w_ivps,
        )
