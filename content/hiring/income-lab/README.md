# Income analysis lab

A fixed public-data snapshot and four reproducible analytical questions. This is a personal portfolio case study, not a live economic release.

## Run

Use Python 3.11 or newer. No extra packages are required.

```sh
python -B -m unittest -v
python -B analyze.py
python -B analyze.py --output-dir results-01
```

Use `py` on Windows or `python3` on macOS/Linux when appropriate. The export directory must not exist. Source inputs are never overwritten.

## Questions and interpretation

`coverage`: Does every quarter have 27 distinct federal units? A row count alone does not protect against duplication; the SQLite primary key also enforces the grain.

`latest_ranking`: Which federal units have the highest and lowest income in the last quarter of this snapshot? This is a descriptive ranking, not an explanation of the gap.

`regional_means`: What is the unweighted mean of the member-state estimates within each region? This is not the official population-weighted regional estimate. Income means must not be summed.

`exact_yoy`: How did each state change compared with the same quarter one year earlier? An explicit join keeps missing prior periods as null instead of silently comparing the wrong observation. Percentage change is not a percentage-point difference.

## Source

IBGE SIDRA table 6472, variable 5933, as stored in repository commit `5810d34116d0e8da9ab10005c561359e73a8560a` of MauricioTaguchi/analise-renda-brasil. Extract recorded by that project: 15 August 2026. Periods: Q2 2021–Q1 2026. Grain: one state per quarter. Currency: Brazilian reais; the source indicator is real average monthly income usually received from all jobs.

https://github.com/MauricioTaguchi/analise-renda-brasil/tree/5810d34116d0e8da9ab10005c561359e73a8560a

The CSV preserves the original proper names. No population weights or sampling uncertainty are supplied here. Do not infer national income by taking the unweighted average of states. New statistical releases can revise historical observations.

## Power BI project

The `power-bi` folder contains an authored PBIP/PBIR report and semantic model source. It has not been opened or refreshed in Power BI Desktop in this delivery. JSON/schema checks are not execution of DAX, Power Query or visual rendering. Follow its acceptance checklist before presenting it as a verified native report. The working browser dashboard is a separate implementation.
