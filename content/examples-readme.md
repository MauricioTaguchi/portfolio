# Reproducible Python learning examples

Author: Maurício Taguchi. All inputs are synthetic. Python 3.11 or later; no third-party packages are needed to run these examples.

## Start here

Extract the entire ZIP into a new folder. Preserve `csv-validation/`, `revisions/` and `run_examples.py` together. Open a terminal in the extracted root.

Windows:

```powershell
py -B run_examples.py
```

macOS / Linux:

```sh
python3 -B run_examples.py
```

The runner executes 38 CSV tests and eight revision tests, checks expected exit codes and diagnostics, and verifies that the input bytes are unchanged. Filesystem-link tests may be skipped if the operating system does not permit creating links; inspect the actual count.

Expected summary: `status: passed`, `valid_fixture_exit: 0`, `invalid_fixture_exit: 1`, `invalid_records: 6`, `diagnostics: 5`, `source_files_unchanged: true`. A temporary report is removed at completion.

To keep a report:

```powershell
mkdir results-session-01
py -B run_examples.py --output-dir results-session-01
```

Use a new directory for another run. `invalid-report.json` must not exist. Reports are created exclusively; existing files and links are refused rather than overwritten. This is not crash-safe atomic publication.

## Read, run, explain

Read the README in each example folder. Then open the matching article:

- https://mauriciotaguchi.com.br/blog/csv-validation.html
- https://mauriciotaguchi.com.br/blog/data-revisions.html
- Resources: https://mauriciotaguchi.com.br/blog/reproduce.html

The revision model is in-memory teaching code, not DataFlow's backend. The CSV contract is deliberately limited; a successful validation is not proof that a sale occurred. Do not substitute business evidence with invented values to make a test pass.

`SHA256SUMS.txt` lists checksums for the package contents, excluding the checksum file itself. No private correspondence, credentials, recordings or event claims are included.
