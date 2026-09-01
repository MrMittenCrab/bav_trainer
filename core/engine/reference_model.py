"""Build the complete reference BAV workbook from standardized financials."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Protection
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from ..data.interface import LineItem, StandardizedFinancials
from ..data.schema import normalize_label

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

DEFAULT_CLASSIFICATION: dict[str, str] = {
    "cash": "Financial Asset",
    "short-term investment": "Financial Asset",
    "accounts receivable": "Operating Working Capital Asset",
    "inventory": "Operating Working Capital Asset",
    "prepaid": "Operating Working Capital Asset",
    "property": "Operating Long-Term Asset",
    "goodwill": "Operating Long-Term Asset",
    "intangible": "Operating Long-Term Asset",
    "accounts payable": "Operating Working Capital Liability",
    "accrued": "Operating Working Capital Liability",
    "deferred revenue": "Operating Working Capital Liability",
    "long-term debt": "Financial Liability",
    "lease": "Operating Long-Term Liability",
}


def _guess_classification(label: str) -> str:
    low = label.lower()
    for key, cat in DEFAULT_CLASSIFICATION.items():
        if key in low:
            return cat
    if "total" in low:
        return ""
    return "Ambiguous — Operating"


class ReferenceModelBuilder:
    """Construct a hidden reference BAV model workbook."""

    def __init__(
        self,
        financials: StandardizedFinancials,
        assumptions: dict[str, Any] | None = None,
    ):
        self.fin = financials
        self.periods = financials.fiscal_years() or financials.period_dates()
        self.assumptions = assumptions or self._default_assumptions()
        self.rowmap: dict[str, Any] = {}

    def _default_assumptions(self) -> dict[str, Any]:
        n = len(self.periods)
        anchor_rev = 1000.0
        if self.fin.income_statement:
            rev_item = self.fin.income_statement[0]
            if self.periods:
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

    def build(self, output_path: Path) -> Path:
        wb = Workbook()
        self._build_source_tabs(wb)
        self._build_condensed(wb)
        self._build_dupont(wb)
        for scenario in ("Bear", "Base", "Bull"):
            self._build_model_tab(wb, scenario)
        self._build_scenario_summary(wb)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output_path)
        sidecar = output_path.with_suffix(".assumptions.json")
        sidecar.write_text(json.dumps(self.assumptions, indent=2) + "\n", encoding="utf-8")
        rowmap_path = output_path.parent / "rowmap.json"
        rowmap_path.write_text(json.dumps(self.rowmap, indent=2) + "\n", encoding="utf-8")
        return output_path

    def _header_block(self, ws, statement: str) -> None:
        ws["A1"] = f"Company: {self.fin.company_name} ({self.fin.ticker})"
        ws["A2"] = f"Statement: {statement}"
        ws["A3"] = f"Units: {self.fin.units}"
        ws["A4"] = f"Source: HK manual ingestion ({self.fin.jurisdiction})"
        ws["A6"] = "Line Item"
        ws["A6"].font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=6, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        ws.column_dimensions["A"].width = 48
        for j in range(len(self.periods)):
            ws.column_dimensions[get_column_letter(2 + j)].width = 16

    def _fill_statement(self, ws, items: list[LineItem], start_row: int = 7) -> int:
        r = start_row
        for item in items:
            ws.cell(row=r, column=1, value=item.label)
            for j, pd in enumerate(self.periods):
                val = item.values.get(pd)
                c = ws.cell(row=r, column=2 + j, value=val)
                c.number_format = NUM_FMT
            self.rowmap.setdefault(normalize_label(item.label), r)
            r += 1
        return r

    def _build_source_tabs(self, wb: Workbook) -> None:
        ws = wb.active
        ws.title = "Income Statement"
        self._header_block(ws, "Income Statement")
        self._fill_statement(ws, self.fin.income_statement)

        ws = wb.create_sheet("Balance Sheet")
        self._header_block(ws, "Balance Sheet")
        bs_start = 7
        self._fill_statement(ws, self.fin.balance_sheet, bs_start)

        ws = wb.create_sheet("Cash Flow Statement")
        self._header_block(ws, "Cash Flow Statement")
        self._fill_statement(ws, self.fin.cash_flow)

    def _find_row(self, tab: str, label_fragment: str) -> int | None:
        for key, row in self.rowmap.items():
            if label_fragment.lower() in key.lower():
                return row
        return None

    def _col_letter(self, period_idx: int) -> str:
        return get_column_letter(2 + period_idx)

    def _build_condensed(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Condensed Financials")
        n_periods = len(self.periods)
        last_col = self._col_letter(n_periods - 1)
        prev_col = self._col_letter(n_periods - 2) if n_periods > 1 else last_col

        ws["A1"] = f"{self.fin.company_name} ({self.fin.ticker}) — Condensed Financials"
        ws["A2"] = "ROE reformulation: classify balance sheet, compute NOPAT and NOA"
        ws.column_dimensions["A"].width = 42
        class_col = get_column_letter(2 + n_periods)

        # Classification table
        r = 4
        ws.cell(row=r, column=1, value="BALANCE SHEET CLASSIFICATION").font = BOLD
        ws.cell(row=r, column=2, value="Classification").font = BOLD
        r += 1
        bs_items = self.fin.balance_sheet
        class_start = r
        dv = DataValidation(type="list", formula1=f'"{",".join(CLASSIFICATIONS)}"', allow_blank=True)
        ws.add_data_validation(dv)
        for item in bs_items:
            if "total" in item.label.lower():
                continue
            ws.cell(row=r, column=1, value=item.label)
            cat = _guess_classification(item.label)
            ws.cell(row=r, column=2, value=cat)
            if cat:
                dv.add(ws.cell(row=r, column=2))
            r += 1
        class_end = r - 1

        # Condensed income (formulas referencing IS)
        r += 1
        ws.cell(row=r, column=1, value="CONDENSED INCOME STATEMENT").font = BOLD
        for j, pd in enumerate(self.periods):
            c = ws.cell(row=r, column=2 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        r += 1
        ni_row = self._find_row("Income Statement", "net income") or self._find_row(
            "Income Statement", "profit"
        )
        rev_row = self._find_row("Income Statement", "revenue") or self._find_row(
            "Income Statement", "turnover"
        )
        pretax_row = self._find_row("Income Statement", "pretax") or self._find_row(
            "Income Statement", "before tax"
        )
        tax_row = self._find_row("Income Statement", "tax")

        rows_spec = [
            ("Net Income", ni_row, False),
            ("Pretax Income", pretax_row, False),
            ("Tax Expense", tax_row, False),
        ]
        row_nums: dict[str, int] = {}
        for label, src_row, bold in rows_spec:
            if not src_row:
                continue
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            for j in range(n_periods):
                col = self._col_letter(j)
                ws.cell(row=r, column=2 + j, value=f"='Income Statement'!{col}{src_row}")
            row_nums[label] = r
            r += 1

        # ETR, NOPAT formulas
        ws.cell(row=r, column=1, value="Effective Tax Rate")
        for j in range(n_periods):
            col = self._col_letter(j)
            if "Tax Expense" in row_nums and "Pretax Income" in row_nums:
                ws.cell(
                    row=r,
                    column=2 + j,
                    value=f"=-{col}{row_nums['Tax Expense']}/{col}{row_nums['Pretax Income']}",
                )
                ws.cell(row=r, column=2 + j).number_format = PCT_FMT
        etr_row = r
        r += 1

        ws.cell(row=r, column=1, value="NOPAT").font = BOLD
        for j in range(n_periods):
            col = self._col_letter(j)
            if "Net Income" in row_nums:
                c = ws.cell(row=r, column=2 + j, value=f"={col}{row_nums['Net Income']}")
                c.fill = GREEN
        nopat_row = r
        r += 1

        self.rowmap["condensed_nopat_row"] = nopat_row

        # Condensed balance sheet aggregates via SUMIF
        r += 1
        ws.cell(row=r, column=1, value="CONDENSED BALANCE SHEET").font = BOLD
        r += 1
        agg_specs = [
            ("NOWC", "Operating Working Capital Asset", "Operating Working Capital Liability", True),
            ("NOA", None, None, True),
            ("Net Debt", "Financial Liability", "Financial Asset", True),
        ]
        for label, pos_cat, neg_cat, bold in agg_specs:
            ws.cell(row=r, column=1, value=label).font = Font(bold=bold)
            for j in range(n_periods):
                col = self._col_letter(j)
                if label == "NOWC":
                    f = (
                        f'=SUMIF($B${class_start}:$B${class_end},"Operating Working Capital Asset",'
                        f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                        f'-SUMIF($B${class_start}:$B${class_end},"Operating Working Capital Liability",'
                        f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                    )
                elif label == "NOA":
                    nowc_r = r - 1
                    f = (
                        f"={col}{nowc_r}+"
                        f'SUMIF($B${class_start}:$B${class_end},"Operating Long-Term Asset",'
                        f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                        f'-SUMIF($B${class_start}:$B${class_end},"Operating Long-Term Liability",'
                        f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                    )
                else:
                    f = (
                        f'=SUMIF($B${class_start}:$B${class_end},"Financial Liability",'
                        f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                        f'-SUMIF($B${class_start}:$B${class_end},"Financial Asset",'
                        f"'Balance Sheet'!{col}{class_start}:'Balance Sheet'!{col}{class_end})"
                    )
                ws.cell(row=r, column=2 + j, value=f)
            if label == "NOWC":
                self.rowmap["condensed_nowc_row"] = r
            if label == "NOA":
                self.rowmap["condensed_noa_row"] = r
            if label == "Net Debt":
                self.rowmap["condensed_netdebt_row"] = r
            r += 1

    def _build_dupont(self, wb: Workbook) -> None:
        ws = wb.create_sheet("ALT DuPont")
        ws["A1"] = f"{self.fin.company_name} — DuPont Decomposition"
        ws["A2"] = "ROE = RNOA + FLEV × Spread"
        ws.column_dimensions["A"].width = 42
        n = len(self.periods)
        r = 4
        ws.cell(row=r, column=1, value="Metric").font = BOLD
        for j, pd in enumerate(self.periods):
            if j == 0:
                continue
            c = ws.cell(row=r, column=1 + j, value=pd)
            c.number_format = "mmm dd, yyyy"
            c.font = BOLD
        r += 1
        nopat_r = self.rowmap.get("condensed_nopat_row", 6)
        noa_r = self.rowmap.get("condensed_noa_row", 24)
        nd_r = self.rowmap.get("condensed_netdebt_row", 28)
        ni_row = self._find_row("Income Statement", "net income") or 13

        metrics = [
            ("RNOA", True),
            ("After-tax CoD", False),
            ("Spread", False),
            ("FLEV", False),
            ("ROE (decomposed)", True),
            ("Actual ROE", False),
        ]
        metric_rows: dict[str, int] = {}
        for j in range(1, n):
            col = self._col_letter(j)
            prev = self._col_letter(j - 1)
            rnoa_row = r
            ws.cell(row=r, column=1, value="RNOA")
            ws.cell(
                row=r,
                column=1 + j,
                value=(
                    f"='Condensed Financials'!{col}{nopat_r}/"
                    f"(('Condensed Financials'!{col}{noa_r}+'Condensed Financials'!{prev}{noa_r})/2)"
                ),
            )
            ws.cell(row=r, column=1 + j).fill = YELLOW
            metric_rows["RNOA"] = rnoa_row
            r += 1

            ws.cell(row=r, column=1, value="Spread")
            ws.cell(
                row=r,
                column=1 + j,
                value=f"={col}{rnoa_row}-0.04",
            )
            metric_rows["Spread"] = r
            r += 1

            ws.cell(row=r, column=1, value="ROE (decomposed)")
            spread_r = r - 1
            ws.cell(row=r, column=1 + j, value=f"={col}{rnoa_row}+1.5*({col}{spread_r})")
            ws.cell(row=r, column=1 + j).fill = YELLOW
            metric_rows["ROE"] = r
            r += 1

            ws.cell(row=r, column=1, value="Actual ROE")
            ws.cell(
                row=r,
                column=1 + j,
                value=(
                    f"='Income Statement'!{col}{ni_row}/"
                    f"(('Balance Sheet'!{col}7+'Balance Sheet'!{prev}7)/2)"
                ),
            )
            r += 1

    def _build_model_tab(self, wb: Workbook, scenario: str) -> None:
        ws = wb.create_sheet(f"Model_{scenario}")
        sc = self.assumptions["scenarios"][scenario]
        ws["A1"] = f"{self.fin.company_name} — {scenario} Scenario"
        ws["A2"] = "10-year residual income (abnormal earnings) model"
        ws.freeze_panes = "B1"
        ws.column_dimensions["A"].width = 42

        ws["A5"] = "Cost of Equity (Ke)"
        ws["B5"] = sc["costOfEquity"]
        ws["B5"].font = BLUE
        ws["B5"].number_format = PCT_FMT
        ws["A6"] = "Terminal Growth (g)"
        ws["B6"] = sc["terminalGrowth"]
        ws["B6"].font = BLUE
        ws["B6"].number_format = PCT_FMT

        headers = ["Metric"] + [f"Y{i}" for i in range(1, 11)]
        for j, h in enumerate(headers):
            ws.cell(row=10, column=1 + j, value=h).font = BOLD

        anchor_col = self._col_letter(len(self.periods) - 1)
        rev_row = self._find_row("Income Statement", "revenue") or 7
        rows = [
            ("Sales", 11),
            ("NOPAT Margin", 12),
            ("NOPAT", 14),
            ("Book Equity", 18),
            ("Abnormal Earnings", 20),
            ("PV Abnormal Earnings", 22),
        ]
        for label, row in rows:
            ws.cell(row=row, column=1, value=label)

        # Y1 sales
        ws.cell(row=11, column=2, value=f"='Income Statement'!{anchor_col}{rev_row}*(1+{sc['growthVector'][0]})")
        ws.cell(row=11, column=2).font = BLUE if scenario == "Base" else None

        # Y1 NOPAT
        ws.cell(row=14, column=2, value="=B11*B12")
        if scenario == "Base":
            ws.cell(row=14, column=2).fill = GREEN

        ws.cell(row=12, column=2, value=sc["marginVector"][0])
        ws.cell(row=12, column=2).font = BLUE
        ws.cell(row=12, column=2).number_format = PCT_FMT

        # IVPS placeholder
        ws.cell(row=38, column=1, value="Intrinsic Value per Share")
        ws.cell(row=38, column=2, value="=B18+SUM(B22:K22)")
        if scenario == "Base":
            ws.cell(row=38, column=2).fill = GREEN

    def _build_scenario_summary(self, wb: Workbook) -> None:
        ws = wb.create_sheet("Scenario_Summary")
        ws["A1"] = f"{self.fin.company_name} — Scenario Summary"
        ws["A3"] = "Scenario"
        ws["B3"] = "Probability"
        ws["C3"] = "IVPS"
        ws["D3"] = "Terminal RNOA"
        for j, h in enumerate(["Scenario", "Probability", "IVPS"], start=1):
            ws.cell(row=3, column=j, value=h).font = BOLD
        for i, name in enumerate(("Bear", "Base", "Bull"), start=4):
            sc = self.assumptions["scenarios"][name]
            ws.cell(row=i, column=1, value=name)
            ws.cell(row=i, column=2, value=sc["probability"])
            ws.cell(row=i, column=2).font = BLUE
            ws.cell(row=i, column=2).number_format = PCT_FMT
            ws.cell(row=i, column=3, value=f"='Model_{name}'!B38")
        ws.cell(row=8, column=1, value="Weighted IVPS")
        ws.cell(row=8, column=5, value="=SUMPRODUCT(B4:B6,C4:C6)")
        ws.cell(row=8, column=5).fill = GREEN
