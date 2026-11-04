# CSV validation: study and rehearsal guide

Maurício Taguchi · English learning resources

## 1. Set up without changing the source

Download the complete examples ZIP from the Reproduce page. Extract it into a new folder and keep the directory structure intact. Python 3.11 or later is required; no extra Python libraries are needed. Open a terminal in the extracted root. Run `py -B run_examples.py` on Windows or `python3 -B run_examples.py` on macOS/Linux.

The runner checks both examples and normally removes its temporary report. To retain a report, create a new directory and use `--output-dir results-session-01`. Never overwrite source records or a previous report merely to make a command succeed.

## 2. Understand the input contract

The exact columns are `sale_id,date,amount_brl`. An ID is nonempty, unique text: `0001` is not converted to `1`. Dates must match `YYYY-MM-DD` and exist in the calendar. Amounts are positive decimals with up to two fractional digits. The currency unit remains Brazilian reais; translating the material does not convert the dataset to dollars.

Positivity is specific to this paid-sales demonstration. Refunds, adjustments and free transactions require a different business contract. Delimiters and decimal separators are explicit, not guessed.

## 3. Explain the five diagnostics

The problematic fixture has six records. ID `0002` occurs twice, producing two duplicate diagnostics. A date is impossible, an amount is missing and an amount is negative, producing the other three diagnostics. The validator does not silently decide which duplicate represents the legitimate sale.

`record` is a logical row count excluding the header. `line_end` refers to the physical file, which matters for quoted fields containing a line break. Reports omit raw cell values, but the source still needs appropriate access controls.

## 4. Interpret completion and exit codes

Exit 0: the complete inspection found no violations of the checked rules. Exit 1: the validator found invalid data or an incomplete validation result. Exit 2: an operational problem prevented normal execution. Read the report's `complete` and `valid` fields rather than treating an exit code as a certification of business truth.

The invalid fixture is expected to return 1. The runner checks that specific expectation and returns 0 only when the full demonstration behaves as documented. A skipped unit test is not an approved test.

## 5. Rehearse the ten-slide sequence

1. Introduce the limited question: is this CSV ready for this analysis?
2. Distinguish opening a file from validating its data.
3. Explain the contract before showing implementation.
4. Inspect the six-record synthetic fixture in a text editor.
5. Run the tests, valid fixture and invalid fixture.
6. Interpret the JSON and codes 0, 1 and 2.
7. Explain the 38 tests, including the eight output-safety regressions.
8. State limits: 10 MiB, 100,000 records, IDs in memory and no business reconciliation.
9. Explain how a reviewer should return to the source before correcting uncertain records.
10. Close with the article, code and an invitation to reproduce the example.

Use the presentation script as a rehearsal aid, not a statement that a talk has already happened. For a personal recording, call it a tutorial or technical demonstration.

## 6. Questions to answer without reading

**Why not keep the first duplicate?** The file alone does not establish which record is authoritative. Both are flagged for an explicit decision.

**Why use Decimal?** The example checks restricted decimal syntax and constructs Decimal directly from text, avoiding an intermediate binary float. This does not make every possible monetary rule correct.

**Why require a new report path?** Different names can refer to the same file through links. Exclusive creation rejects existing destinations and prevents overwriting. An interrupted new write can still be incomplete.

**Does a successful test validate future data?** No. It provides evidence for the implementation and tested inputs. Future inputs and changed business rules need their own checks.

**Why does undo create a new revision?** Content identity and operation history are different. Restoring old bytes can still be a new event. The teaching model does not verify concurrent database behavior.

**What does an offline SDK check prove?** Controlled behavior with fixtures. It does not prove availability of the public API. A live run is a separate observation at a particular time.

## 7. A safe practice exercise

Make a new synthetic CSV rather than changing the original fixture. Add one impossible date, one extra column and an identifier with leading zeroes. Run the validator and explain each outcome. Do not invent corrections for real records when the source evidence is missing.

Record the command, input version, expected behavior, actual behavior and any skipped tests. A small documented difference is more useful than an unexplained green result.

## 8. Prepare an honest public demonstration

Close private messages, personal files and terminals containing secrets. Use only the synthetic examples. Check audio, text size and screen capture before recording. Review the entire recording before publishing.

A demonstration has not been recorded or delivered by the preparation of these files. Add a video link only after it exists. Add event details, an audience and feedback only after the activity actually takes place, with the relevant permissions.

## References and materials

Articles and downloads: https://mauriciotaguchi.com.br/blog/reproduce.html

Python CSV: https://docs.python.org/3/library/csv.html

Python Decimal: https://docs.python.org/3/library/decimal.html

DataFlow receipt design: https://github.com/MauricioTaguchi/data-analytics-platform/blob/main/docs/AUDIT_RECEIPTS.md
