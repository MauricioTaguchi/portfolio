# Technical blog maintenance

The blog is a static addition to the existing portfolio, not a replacement application. Its source is `public/blog/`; `docs/blog/` is the identical published copy. The existing React bundle, project images, domain settings and third-party notices are unchanged.

## Editing an article

Edit the matching HTML file in `public/blog/`. Keep the visible date honest and add an updated date when a material revision is made. Each tutorial links to its source and tests. Distinguish a conceptual example, an offline test and a live integration check.

For an article-only change, copy the changed file to the same relative path under `docs/blog/`. For a normal full site build, the existing Vite build copies the public directory into docs. Do not edit only docs: a later build would discard the change.

The home page entry is in both source `index.html` and the current `docs/index.html`. Its scoped CSS lives at `public/blog-entry.css` and `docs/blog-entry.css`. The source HTML keeps the entry in future builds without changing React components.

## Verification

From the repository root:

```sh
python -B scripts/check_blog.py
python -B -m unittest discover -s public/blog/exemplos/validacao-csv -v
python -B -m unittest discover -s public/blog/exemplos/revisoes -v
```

Use `-B` to avoid copying Python bytecode caches into public assets. Do not commit local reports or caches. The workflow performs the same checks.

The validator has 30 tests; the in-memory revision model has eight. Those tests are not the DataFlow integration suite. The SDK article links to the actual SDK workflow evidence and states that no new live API test was run for that article.

Local browser checks rendered the five pages at desktop and mobile widths and inspected local links and an anchor interaction. Environment policy blocked HTTP navigation in that browser; a complete deployed-site navigation/download test was not performed there.

## Publishing and rollback

This repository documents GitHub Pages publishing from main and /docs. Confirm the deployment result rather than assuming a merge is already live. A source/HTML change to the existing app still requires the normal documented build when it changes generated assets.

To roll back this addition, revert its merge commit through a new commit; do not reset or force-push the repository. Keep any independent changes made after publication.

Never publish client information, private correspondence, credentials or claims about talks that have not happened. A collection of new posts is not a long-term publication history.
