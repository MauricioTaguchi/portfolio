# Sales CSV validation

A teaching example using synthetic data and the Python standard library. Requires Python 3.11 or later. It contains no company or client records.

## Run

Open a terminal in this directory. On Windows, use `py` instead of `python` where appropriate.

```sh
python -B -m unittest -v
python -B validate_sales.py sales_valid.csv
python -B validate_sales.py sales_invalid.csv --output report.json
```

The valid fixture exits with 0. The invalid fixture exits with 1 intentionally: six records produce five diagnostics, including both occurrences of the duplicated ID. Exit code 2 means an input, configuration or writing problem. The command neither corrects nor rewrites the source.

Contract: exact columns `sale_id,date,amount_brl`, in that order; a nonempty unique text ID; a real `YYYY-MM-DD` date; a positive decimal amount with up to two fractional digits. Thousands separators, currency symbols and scientific notation are rejected. Outer whitespace is ignored for validation only; leading zeroes in IDs are preserved. Positive amounts represent paid sales in this particular example. Refunds need a different contract.

For a semicolon-delimited file with comma decimals, explicitly select:

```sh
python -B validate_sales.py sales.csv --delimiter ";" --decimal-separator ","
```

For a row-level issue, `record` gives the data row number, starting at 1 after the header. A header mismatch or an empty dataset is reported as record 0. `records_checked` gives the total number of data rows checked. `line_end` gives the last physical line read for the issue. A quoted field can span several lines. `complete: false` means parsing or limits prevented full inspection, not that the file was approved.

## Limits

At most 10 MiB and 100,000 records, with IDs retained in memory. File size is checked before reading; this does not protect against concurrent modification. The example does not prove a sale's existence, reconcile totals, validate tax obligations or provide authorization. It is not a hostile-file security boundary.

Diagnostics include field names and positions, not raw CSV values. Keep real data access restricted and never publish personal records in an issue.

## Report preservation

`--output` requires a new path. Existing files, symbolic links and hard links are refused even under a different name. Exclusive creation avoids overwriting an existing destination, but is not crash-safe atomic publication.

`test_output_safety.py` adds eight regression cases to the 30 original tests. Keep both test files present. Link-related tests may be skipped on systems that do not support or permit them; report the actual result.

References: https://docs.python.org/3/library/csv.html and https://docs.python.org/3/library/decimal.html.
