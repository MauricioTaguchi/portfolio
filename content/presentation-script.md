# Presentation script: Is your CSV ready for analysis?

Maurício Taguchi · Rehearsal material, not a record of a delivered presentation.

Suggested running time for your own demonstration: 10–15 minutes.

## Slide 1 — Is your CSV ready for analysis?

Hello, I’m Maurício Taguchi. I’ll show a small check you can run before using a CSV in a dashboard. This example uses synthetic data and the Python standard library. The goal is not to clean everything automatically, but to produce a diagnosis someone else can reproduce. Present a solo recording as a tutorial, not as an event talk.

## Slide 2 — Opening is not validating.

Distinguish being able to open a file from trusting the analysis. A duplicate may count a sale twice, an impossible date can break grouping, and an empty amount can be skipped in aggregation. These are illustrative risks, not measured client results. Invite the audience to consider which cases they have encountered.

## Slide 3 — Start with the contract.

Explain the contract before the code. ID 0001 remains text. The date must match the format and exist in the calendar. amount_brl represents Brazilian reais, not dollars. Positive amounts model paid sales in this example; refunds need a different contract. Outer whitespace is ignored for validation only; no source data is rewritten.

## Slide 4 — Small input. Visible problems.

Open sales_invalid.csv in a text editor, not a spreadsheet that may convert identifiers. There are six records. ID 0002 appears twice. February 30 does not exist. One amount is missing and another is negative. Both duplicate occurrences are flagged, which is why the report has five diagnostics. Do not silently choose which duplicate to keep.

## Slide 5 — Three commands to start.

Open a terminal inside the csv-validation folder in the downloaded package. Check the Python version. Run the tests, then the valid and invalid fixtures. On PowerShell, inspect $LASTEXITCODE immediately after each command. The invalid fixture intentionally returns 1. Use a new report name: existing files, symbolic links and hard links are refused with code 2. Exclusive creation prevents overwriting but is not crash-safe atomic publication.

## Slide 6 — Read the result, not just the code.

Open the generated JSON. Distinguish valid from complete: a complete read can still find invalid records, while an incomplete inspection is not approval. record counts logical records excluding the header; line_end counts physical lines including multiline quoted fields. The report omits raw cell values. The runner knows the invalid fixture should exit with 1 and checks that expectation.

## Slide 7 — Test what can go wrong, too.

The CSV suite contains 38 tests. Explain two behaviors: all duplicate occurrences are flagged, and the input hash remains unchanged. The eight output-safety regressions exercise existing destinations and links. Link-related tests may be skipped on systems that do not permit them; report the actual count. Tests describe this implementation and these inputs, not every possible future file.

## Slide 8 — Validation has boundaries.

State the boundaries without presenting the example as a production product. Size is checked before reading and does not defend against concurrent changes or all hostile inputs. We do not reconcile sales or check tax rules. Refund and free-sale policies require agreement with the business.

## Slide 9 — Diagnostics need a decision.

Practice with a separate synthetic copy. Resolve a duplicate through an explicit decision about the authoritative record, not an invented ID that hides the issue. In real data, obtain missing values from a trusted source and clarify the meaning of negative transactions. When evidence is missing, return to the source rather than manufacturing a correction.

## Slide 10 — Validation provides evidence. The business decides.

Invite the reader to reproduce the example and propose a rule with a test case. References are the official Python csv and decimal documentation. These materials do not establish that a talk, audience or community activity occurred. Record real teaching activity and feedback only after they happen.

## Before publishing a recording

Use synthetic inputs, close private applications, check audio and screen legibility, and review the entire video. Publish a video link only after the recording exists and has been reviewed.
