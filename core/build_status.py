"""Readable progress derived from emitted semantic families, not release claims."""
from collections import Counter
from openpyxl.styles import Font, Alignment

ACTIVE = 'Active / available'
UNAVAILABLE = 'Source unavailable / not admitted'
INACTIVE = 'Implementation / family not active'

# Groups describe implemented identities, not roadmap acceptance.
GROUPS = (
    ('Geographic Analysis', 'Revenue mix', ('geographic_revenue_share',)),
    ('Geographic Analysis', 'Revenue growth contribution', ('geographic_revenue_growth_contribution',)),
    ('Geographic Analysis', 'Margin bridge', ('geographic_operating_margin_contribution',)),
    ('Geographic Analysis', 'Operating-profit amount bridge', ('geographic_operating_profit_amount_change',)),
    ('Geographic Analysis', 'Revenue/margin effects', ('geographic_operating_profit_revenue_effect', 'geographic_operating_profit_margin_effect')),
    ('Geographic Analysis', 'Incremental margin', ('geographic_operating_profit_incremental_margin',)),
    ('Geographic Analysis', 'Operating-profit growth contribution', ('geographic_operating_profit_growth_contribution',)),
    ('Operating KPIs', 'Store-count history', ('store_count_source',)),
    ('Operating KPIs', 'Store-count change', ('store_count_net_change',)),
    ('Operating KPIs', 'Store-count growth', ('store_count_growth',)),
    ('Operating KPIs', 'Revenue/store growth comparison', ('operating_kpi_revenue_store_growth_difference',)),
    ('Operating KPIs', 'Comparable Sales Analysis', ('operating_kpi_comparable_sales_source',)),
    ('Operating KPIs', 'Sales per Square Foot Analysis', ('operating_kpi_sales_per_square_foot_source',)),
    ('Operating KPIs', 'Revenue per Store Analysis', (
        'revenue_per_store_period_end',
        'revenue_per_store_average',
        'revenue_per_store_change',
        'revenue_per_store_growth',
    )),
    ('Revenue drivers', 'Revenue Driver Analysis', (
        'revenue_driver_store_growth',
        'revenue_driver_revenue_growth',
        'revenue_driver_store_difference',
        'revenue_driver_comparable_sales',
        'revenue_driver_comparable_sales_difference',
        'revenue_driver_revenue_per_store',
        'revenue_driver_geographic_contribution',
    )),
)


def status_rows(smap):
    from .engine.build_contract import BUILD_MODULES
    modules = {m.id: m for m in BUILD_MODULES}
    components = smap.all_ordered()
    counts = Counter(c.family_id for c in components)
    rows = []
    special_tabs = {c.tab for c in components if c.family_id.startswith(('geographic_', 'operating_kpi_', 'store_count_', 'revenue_per_store_', 'revenue_driver_'))}
    for tab in dict.fromkeys(c.tab for c in components):
        if tab not in special_tabs:
            rows.append(dict(group='Historical analysis', family=tab, status=ACTIVE,
                             cells=sum(c.tab == tab for c in components)))
    for group, title, families in GROUPS:
        total = sum(counts[f] for f in families)
        module = modules.get(
            'geographic' if group == 'Geographic Analysis'
            else 'revenue_driver' if group == 'Revenue drivers'
            else 'operating_kpi'
        )
        integrated = bool(module and module.workbook_capable and module.prepare and module.writers
                          and module.status != 'deferred'
                          and (module.current_ready or (module.status == 'complete' and module.complete_analysis)))
        status = ACTIVE if total else (UNAVAILABLE if integrated else INACTIVE)
        rows.append(dict(group=group, family=title, status=status, cells=total))
    return rows


def add_build_status(wb, smap):
    if 'Build Status' in wb:
        del wb['Build Status']
    ws = wb.create_sheet('Build Status', 1)
    ws.append(['Current Progress — development snapshot'])
    ws.append(['Availability applies to this build; it does not establish parent or release acceptance.'])
    ws.append(['Active may cover only admitted periods. See analytical schedules for gaps.'])
    ws.append(['Area', 'Family / module', 'Status', 'Mapped cells'])
    for row in status_rows(smap):
        ws.append([row['group'], row['family'], row['status'], row['cells']])
    for col, width in [('A',25), ('B',44), ('C',40), ('D',16)]:
        ws.column_dimensions[col].width = width
    ws.freeze_panes = 'A5'
    ws.sheet_view.showGridLines = False
    for row in ws:
        for cell in row:
            cell.font = Font(name='Aptos Narrow', size=11)
            cell.alignment = Alignment(vertical='top')
    for sheet in ('Overview', 'Trainer'):
        if sheet in wb:
            wb[sheet]['G1'] = 'Current Progress'
            wb[sheet]['G1'].hyperlink = "#'Build Status'!A1"
