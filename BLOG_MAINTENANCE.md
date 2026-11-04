# Technical blog maintenance

The blog source is `public/blog/`; `docs/blog/` is its byte-identical published copy. The existing application, images, domain configuration and third-party notices are preserved. The homepage entry remains in source `index.html` and `docs/index.html` with the existing scoped stylesheet.

## Edit and reproduce

Edit the source HTML and keep publication dates honest. Update `public/blog/sitemap.xml` when adding a page; copy the changed files to the identical paths under `docs/blog/`. A normal Vite build copies the public directory automatically. Do not edit only `docs/`.

From the repository root, with Python 3.11 or later:

```sh
python -B scripts/check_blog.py
python -B -m unittest discover -s tests -v
python -B public/blog/exemplos/run_examples.py
```

The example runner executes 38 CSV tests and eight revision tests, validates fixture exit codes and JSON, and verifies that fixture bytes are unchanged. Link-related tests may skip on operating systems that do not permit creating links; report skips explicitly. Reports use a temporary directory by default. To retain a report, provide an existing directory with `--output-dir`; `invalid-report.json` must not already exist.

The CSV CLI creates output exclusively: existing files, hard links and symlinks are refused. This prevents overwriting existing destinations, but is not crash-safe atomic publication. Keep source directories trusted and inspect a command's exit code before consuming a report.

The static verifier discovers pages rather than hard-coding their count. It checks resource URLs, anchors, metadata, sitemap membership and mirror bytes. It rejects bytecode caches and works with `python -O`; validation does not depend on removable assert statements. Eight independent regression tests exercise the verifier.

## Browser verification

Browser tests are separate from the dependency-free examples:

```sh
python -m pip install playwright==1.57.0
python -m playwright install chromium
python -B scripts/check_blog_browser.py
```

On Linux CI, install Chromium with `--with-deps`. `BROWSER_EXECUTABLE` can select an already installed Chromium. The test starts an ephemeral local server, visits every blog page at 1440x1000 and 390x844, checks content, console health, styles and overflow, then clicks through article/language navigation, a contents anchor, a practice answer and a real download. Downloaded bytes are compared with the checked-out version. It does not exercise the rest of the React application.

A navigation restriction is a failure, not a reason to silently skip or claim a browser pass. The local authoring environment may only support in-memory rendering; that visual preview is not HTTP evidence.

The read-only `Blog checks` workflow runs example/verifier tests with Python 3.11 and 3.13 and performs the Chromium HTTP checks. `Published blog checks` runs after a successful main-branch Pages deployment, checks out that deployment's commit and verifies the public domain:

```sh
python -B scripts/check_blog_browser.py --base-url https://mauriciotaguchi.com.br/blog/
```

A deployment success and a browser success are different results. Read the actual run and individual steps before claiming either. A public-site failure can reflect DNS, CDN propagation, network policy or a real regression; inspect it rather than suppressing it. No schedule or continuous monitoring is configured.

## Publishing, evidence and rollback

Use a small branch and pull request. Check the test results before merging and the Pages and published-domain results afterward. Revert through a new commit when needed; do not reset or force-push history. Keep later independent changes.

These teaching tests are not the DataFlow integration suite. The SDK has its own offline and live verification boundaries. Never publish private correspondence, credentials or client data. Do not invent talks, an audience, upstream acceptance or a sustained publication history. The practice page provides preparation, not proof of an event.
