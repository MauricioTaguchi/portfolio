# Technical blog maintenance

The blog source is `public/blog/`; `docs/blog/` is its byte-identical published copy. The existing application, images and third-party notices are preserved. The homepage entry remains in source `index.html` and `docs/index.html` with the existing scoped stylesheet.

## Edit and reproduce

Edit the source HTML and keep publication dates honest. Update `public/blog/sitemap.xml` when adding a page; copy the changed files to the identical paths under `docs/blog/`. A normal Vite build copies the public directory automatically. Do not edit only `docs/`.

From the repository root, with Python 3.11 or later:

```sh
python -B scripts/check_blog.py
python -B scripts/check_publication.py
python -B -m unittest discover -s tests -v
python -B public/blog/exemplos/run_examples.py
```

The example runner executes 38 CSV tests and eight revision tests, validates fixture exit codes and JSON, and verifies that fixture bytes are unchanged. Link-related tests may skip on operating systems that do not permit creating links; report skips explicitly. Reports use a temporary directory by default. To retain a report, provide an existing directory with `--output-dir`; `invalid-report.json` must not already exist.

The CSV CLI creates output exclusively: existing files, hard links and symlinks are refused. This prevents overwriting existing destinations, but is not crash-safe atomic publication. Keep source directories trusted and inspect a command's exit code before consuming a report.

The static verifier discovers pages and checks resource URLs, anchors, metadata, sitemap membership and mirror bytes. It rejects bytecode caches and works with `python -O`. Eight regression tests exercise it. A further 18 publication tests cover build-critical assets, stale responses, bounded retries, file inventory and redirect boundaries. These maintenance tests are separate from the 46 tutorial tests.

## Preserve the custom domain during builds

`public/CNAME` is the source of the unchanged custom domain; it must match `docs/CNAME`. Vite empties the build directory, so keeping the file only in `docs/` loses it on a clean build. Never change the hostname as a workaround for a failing check.

The CI build job installs the exact package-manager version declared in `package.json`, uses the frozen lockfile and runs the real `pnpm build`. Afterward, it checks the blog mirror, domain file, homepage blog link and stylesheet copies. Generated build output is tested in the runner; the workflow does not push it back to the repository.

## Browser verification

Browser tests are separate from the dependency-free examples:

```sh
python -m pip install playwright==1.57.0
python -m playwright install chromium
python -B scripts/check_blog_browser.py
```

On Linux CI, install Chromium with `--with-deps`. `BROWSER_EXECUTABLE` can select an already installed Chromium. The test starts an ephemeral local server, visits every blog page at 1440x1000 and 390x844, checks content, console health, styles and overflow, then exercises article/language navigation, an anchor, a practice answer and a real download. Downloaded bytes are compared with the checkout. This is not full behavioral regression testing of the React application.

A navigation restriction is a failure, not a reason to silently skip or claim a browser pass. In-memory rendering is a visual preview, not HTTP evidence.

## Verify the published version, not just a successful deployment

`Published blog checks` runs on relevant pushes to `main` or a manual main-branch run. It no longer relies on a Pages-generated `workflow_run` event. It has read-only repository permission and no schedule. New runs cancel superseded ones.

Before opening the browser, it checks local publication invariants and waits at most 180 seconds for every blog asset on the HTTPS domain to match this checkout byte for byte. Missing/stale responses are retried with a delay; persistent differences fail the job. It then performs the real browser navigation and downloads:

```sh
python -B scripts/check_publication.py --remote
python -B scripts/check_blog_browser.py --base-url https://mauriciotaguchi.com.br/blog/
```

A deployment success and a browser success are different results. Read the actual run and individual steps before claiming either. A failure can reflect deployment failure, propagation, network restrictions or a regression. Inspect it rather than suppressing it. A successful run is evidence for that version and time, not a future availability guarantee.

## Publishing, evidence and rollback

Use a small branch and pull request. Check the test results before merging and the Pages and published-domain results afterward. Revert through a new commit when needed; do not reset or force-push history. Keep later independent changes.

These teaching tests are not the DataFlow integration suite. The SDK has separate offline and live evidence. Never publish private correspondence, credentials or client data. Do not invent talks, an audience, upstream acceptance or a sustained publication history. The practice page is preparation, not proof of an event.

## English content and learning resources

All public editorial content is now in English, including the portfolio, labels, accessibility text, articles and learning resources. Canonical article URLs use English names. The five previous article/practice URLs remain as one-step redirects with canonical targets and noindex metadata. Do not add redirect chains or include aliases in the sitemap.

The desktop and mobile navigation both include Blog. The Reproduce page groups the examples ZIP, the ten-slide PowerPoint and the study/presentation guides. There is no empty events section and no claim of a delivered presentation.

The reviewed learning sources live in `content/`. To regenerate downloads before a site build:

```sh
python -m pip install python-pptx==1.0.2
python -B scripts/build_learning_resources.py
pnpm build
python -B scripts/check_blog.py
python -B scripts/check_publication.py
python -B -m unittest discover -s tests -v
python -B public/blog/exemplos/run_examples.py
```

The generator uses an explicit public-file allowlist. It never packages email drafts, personal correspondence, credentials, private reports or font files. The examples ZIP runs independently of the repository and contains English folder names. Its validator logic is byte-identical to the documented source. Report creation remains exclusive, not crash-safe atomic publication.

When translating or changing labels, update the browser checks to match the interface without dropping behavior checks. The checks now exercise the main-menu Blog link, canonical English articles, legacy redirects and every learning-resource download. The slide deck and speaker script are preparation materials; record a video, audience or event only after it actually exists.
