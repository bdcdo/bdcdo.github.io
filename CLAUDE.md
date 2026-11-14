# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a personal academic website built with Jekyll using the al-folio theme. The site is hosted on GitHub Pages and contains pages for showcasing publications, research projects, teaching experience, CV, and blog posts.

## Setup

```bash
npm ci                    # Prettier 3.1.1 + @shopify/prettier-plugin-liquid, pinned in package.json
uvx pre-commit install    # hooks from .pre-commit-config.yaml (needs uv; `pip install pre-commit` also works)
bundle install            # Ruby 3.2.2 (the version CI uses) for the Jekyll build
```

`uv` is also needed for `bin/subconjunto-icones.py`, which declares its dependency (fonttools) inline; `bin/baixa-roboto.py` only needs the Python standard library.

## Checks

There is no test suite. The checks are the ones CI runs:

```bash
npx prettier . --check                     # lint (workflow prettier.yml); fix with `npx prettier . --write`
uv run bin/subconjunto-icones.py --check   # icon font subsets up to date (workflow icones.yml)
JEKYLL_ENV=production bundle exec jekyll build   # build (workflow deploy.yml builds on every PR that touches the site)
```

The pre-commit hook runs the first two in about 15 s, plus the hygiene hooks (trailing whitespace, end of file, YAML, large files) on the staged files. To run the lint hooks over the whole repo use `uvx pre-commit run prettier --all-files` and `uvx pre-commit run subconjunto-icones --all-files`. Do not run `pre-commit run --all-files` with every hook: the hygiene hooks rewrite vendored minified files (`assets/js/*.min.js`, `assets/css/bootstrap.min.css`, source maps) and a few others that are committed as they are.

## Development Commands

### Local Development

To run the site locally:

```bash
# Using Jekyll directly
bundle exec jekyll serve --livereload

# Using Docker (recommended)
docker-compose up
```

The site will be available at `localhost:8080` (Docker) or `localhost:4000` (Jekyll direct).

### Build the Site

```bash
# Using Jekyll directly
JEKYLL_ENV=production bundle exec jekyll build

# Using Docker
docker-compose run jekyll jekyll build
```

### Style Formatting

```bash
# Format every file Prettier handles (Liquid, HTML, Markdown, YAML, JS, SCSS); .prettierignore lists the exceptions
npx prettier . --write
```

## Technical Architecture

The site is built with Jekyll, a static site generator. Key components:

1. **Configuration**: `_config.yml` contains all site configuration, including social media profiles, layout settings, and plugin configurations.

2. **Content Structure**:

   - `_pages/`: Main pages (about, cv, projects, publications, teaching, blog, news, 404)
   - `_posts/`: Blog posts
   - `_projects/` and `_news/`: collections declared in `_config.yml`; the folders do not exist yet and are created with the first item
   - `_bibliography/`: Bibliography files for publications (`refs-pt.bib`, `refs-en.bib`, `preprints-pt.bib`, `preprints-en.bib`; `_pages/publications.md` renders each one)
   - `_data/`: Structured data files (coauthors.yml, cv.yml, venues.yml)

3. **Theme Structure**:

   - `_layouts/`: Page layout templates
   - `_includes/`: Reusable components
   - `_sass/`: SCSS styling files
   - `_plugins/`: Ruby Liquid filters and generators (e.g. `cache-bust.rb`, `image-dimensions.rb`)
   - `assets/`: Static assets (images, CSS, JavaScript, PDFs, fonts)
   - `_fonts-completas/`: full icon fonts (Font Awesome, Academicons, Tabler); only the subsets in `assets/` are served

4. **Scripts** (`bin/`):

   - `subconjunto-icones.py`: regenerates the icon font subsets in `assets/` from `_fonts-completas/`. Run `uv run bin/subconjunto-icones.py` and commit the result whenever a template starts using an icon class (`fa-*`, `ai-*`, `ti-*`) that no file cited before; CI fails otherwise.
   - `baixa-roboto.py`: downloads Roboto into `assets/fonts/roboto/` and writes `assets/css/roboto.css` (generated, do not edit by hand).

5. **Deployment**:
   - `.github/workflows/deploy.yml` builds the site and, on push to `master`, publishes `_site` to the `gh-pages` branch (GitHub Pages, custom domain in `CNAME`)
   - The workflow only runs for the paths listed in its `paths` filter; a new top-level folder that changes the generated HTML needs an entry there
   - Docker is configured for consistent local development

## Conventions

- Default branch `master`; work goes through PRs from a topic branch (Portuguese, kebab-case, e.g. `cache-bust-main-css`).
- Commit messages and PR titles in Portuguese, describing the change in a full sentence (e.g. "Cache do main.css: o filtro bust_css_cache passa a ler \_sass/ ..."). Code comments and new scripts are also in Portuguese.
- Every file Prettier handles must pass `npx prettier . --check` (printWidth 150, Liquid plugin).
- GitHub Actions are pinned by full commit SHA with the version in a comment; Dependabot proposes updates monthly with a 7-day cooldown.
- Generated files (icon subsets, `assets/css/roboto.css`) are produced by the scripts in `bin/`, not edited by hand.

## Common Tasks

### Adding a New Publication

1. Add the publication to the appropriate `.bib` file in `_bibliography/` (Portuguese and English versions are separate files)
2. Add any preview images to `assets/img/publication_preview/`
3. Add related PDFs to `assets/pdf/`

### Adding a New Project

Create a new Markdown file in `_projects/` with the appropriate front matter.

### Adding News Items

Create a new Markdown file in `_news/` with the appropriate front matter.

### Updating CV Information

Edit the YAML files in `_data/` directory to update CV information, coauthors, etc.

### Changing Site Configuration

Edit `_config.yml` to modify site settings, social media links, and plugin configurations.
