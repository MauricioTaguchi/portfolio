# Brazil Income in Power BI Desktop

Validated on 4 November 2026 in Microsoft Power BI Desktop for Windows, version 2.159.1231.0. The saved report opens with Q1 2026 selected and all regions included.

[Download the validated PBIX](BrazilIncome_Validado.pbix) · [View the report screenshot](BrazilIncome_Q1_2026.png) · [See all 15 DAX results](BrazilIncome_15_testes.png)

## Desktop results

Refresh loaded 540 state-quarter observations across 27 federal units and 20 quarters. The DAX query returned 15 rows marked `OK`, including the check for duplicate state-quarter keys. The evidence image shows the top and bottom of the same result grid, with row 8 visible in both views.

| Scope | Result |
| --- | --- |
| Q1 2026, all regions | Mean BRL 3,437.41, 27 federal units and 6.81% year-over-year growth |
| Q1 2026, Southeast | Mean BRL 3,971.50 and four federal units. The bar chart showed Espírito Santo, Minas Gerais, Rio de Janeiro and São Paulo. |
| Q1 2026, Distrito Federal | The state-filtered DAX check returned BRL 6,720.00 and one federal unit. |
| Q2 2021, all regions | The year-over-year card was blank. The snapshot starts in this quarter. |

Both slicers, all three cards, the state bar chart and the quarterly trend rendered in Desktop. Filtering to one quarter left one point on the trend. The income card abbreviates reais in thousands. The DAX grid reports the mean to two decimal places.

## Reproduce the checks

1. Open `BrazilIncome_Validado.pbix` in Power BI Desktop, or open `BrazilIncome.pbip` beside its Report and SemanticModel directories.
2. Select **Home → Refresh**. The embedded import tables use a fixed snapshot of IBGE SIDRA table 6472, variable 5933, covering Q2 2021 through Q1 2026. Refresh reloads that snapshot.
3. In DAX query view, select the **Validar_BrazilIncome** tab and run the full query. If needed, open a new query and paste the [validation DAX file](BrazilIncome.SemanticModel/DAXQueries/Validar_BrazilIncome.dax).
4. In report view, select the quarters and regions above. The Distrito Federal assertion is part of the DAX query. To see all quarters on the trend, clear the quarter slicer.

The model filters Income through the States and Quarters dimensions. The mean gives equal weight to each represented federal unit. An official national estimate requires population weights. The validated file uses the snapshot from [income pipeline commit 5810d34](https://github.com/MauricioTaguchi/analise-renda-brasil/tree/5810d34116d0e8da9ab10005c561359e73a8560a).
