# Power BI project source — Desktop validation pending

This is an authored PBIP/PBIR source project, not a verified PBIX or a published service report. The current delivery environment did not expose the installed plugin's browser controls. DAX, Power Query refresh, interactions and rendering have NOT been executed inside Power BI.

The model contains 540 income observations, 27 state dimension rows and 20 quarter rows. Its M partitions embed the exact reviewed snapshot, so no file paths, account credentials or live API access are required. Embedded data is intentionally static. The model has one-to-many state and quarter relationships, with single-direction filtering. State means are not additive.

## Acceptance checklist in Power BI Desktop

1. Open BrazilIncome.pbip with a Power BI Desktop version supporting PBIP and PBIR.
2. Refresh the embedded import tables. Confirm 540 Income, 27 States and 20 Quarters rows.
3. Check the two relationships and sort Quarters[quarter] by quarter_code.
4. Inspect every visual; correct any reported schema/visual compatibility errors before publishing.
5. Select Q1 2026 and all regions. The unweighted state mean should be BRL 3,437.41. This is NOT the official national average.
6. Filter to Distrito Federal. Q1 2026 income should be BRL 6,720.00. Select Q2 2021: the prior-year comparison must be blank.
7. Check that the quarter slicer limits the trajectory; clear it to see the full snapshot. Measures use the latest selected quarter when more than one is selected.
8. Save the verified report as PBIX only after refresh and visual checks. Record the actual Desktop version and result; do not mark this checklist complete in advance.

The browser dashboard is a separate, tested implementation, not a substitute for these native checks. No account, workspace, license purchase or Publish to web operation has been created.

References:
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset
