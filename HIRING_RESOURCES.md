# Hiring resources

English recruiter entry points are in src/portfolio.tsx. Resume facts live in content/hiring/resume.json; do not silently change employment dates or claim new experience. The public résumé intentionally omits a phone number and street address.

Build the document, case studies and analytics kit:

```sh
python -m pip install reportlab==4.4.9
python -B scripts/build_power_bi_source.py
python -B scripts/build_hiring_resources.py
pnpm build
python -B -m unittest discover -s tests -v
python -B scripts/check_hiring_browser.py --evidence-dir /tmp/hiring-evidence
```

The standalone income lab has 12 additional tests, run from content/hiring/income-lab with `python -B -m unittest -v`. It uses a pinned historical CSV, not a live feed. Do not substitute refreshed values while retaining the old source date or checksum. Refresh the original income pipeline, review its metadata, and replace the snapshot intentionally.

The Power BI files are authored project sources. They must be opened, refreshed and visually checked in Power BI Desktop before claiming a verified native report. Static JSON checks cannot run DAX or M. The browser income dashboard is a separate implementation.

DataFlow's isolated frontend is built from an explicit commit with `python -B scripts/build_dataflow_demo.py`. This requires public GitHub access and the declared Node/pnpm toolchain. It adds a demo-only request interceptor, disables file input and API connection, and preserves third-party notices. It does not deploy the backend, create accounts or verify durable process recovery. Review the pin before rebuilding. Normal portfolio builds reuse the checked-in static demo assets.

After changes, check the actual CI result, Pages deployment and published hiring-resource checks. Do not infer a public pass merely from a local build. Screenshots and run logs belong in short-lived build artifacts, not source. No application emails, job submissions, periodic tasks or fictitious speaking records are produced by these scripts.
