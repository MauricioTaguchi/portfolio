# Maurício Taguchi — Portfolio

Personal portfolio and technical blog covering data analytics, automation, engineering and development. All public editorial content and learning resources are in English.

## Development

Use Node.js 24 and the package manager declared in `package.json`.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

## Build and publish

```sh
python -m pip install python-pptx==1.0.2
python -B scripts/build_learning_resources.py
pnpm build
python -B scripts/check_blog.py
python -B scripts/check_publication.py
```

The static site is generated into `docs/`. GitHub Pages publishes `main` and `/docs`. The custom domain is preserved through `public/CNAME`. Commit the regenerated publication files with each source change. Keep the existing dependency lockfile and restricted build-hook approval.

## Reading and learning

The desktop and mobile menus link directly to the blog. The Reproduce page provides the complete examples ZIP, an editable slide deck and a study guide. Legacy article addresses remain available as English redirects; canonical addresses use English names. No talks, audience or sustained publication history are implied by these resources.

See `BLOG_MAINTENANCE.md` for verification and maintenance. The contact form prepares a message locally and offers clipboard copying and a LinkedIn link; it does not send email or store form data on a server. Project screenshots use demonstration data.

Third-party licenses and notices remain applicable.
