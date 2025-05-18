# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a personal academic website built with Jekyll using the al-folio theme. The site is hosted on GitHub Pages and contains pages for showcasing publications, research projects, teaching experience, CV, and blog posts.

## Development Commands

### Local Development

To run the site locally:

```bash
# Using Jekyll directly
bundle exec jekyll serve --livereload

# Using Docker (recommended)
docker-compose up
```

The site will be available at http://localhost:8080 (Docker) or http://localhost:4000 (Jekyll direct).

### Build the Site

```bash
# Using Jekyll directly
JEKYLL_ENV=production bundle exec jekyll build

# Using Docker
docker-compose run jekyll jekyll build
```

### Style Formatting

```bash
# Format liquid templates
npx prettier --write "**/*.liquid"
```

## Technical Architecture

The site is built with Jekyll, a static site generator. Key components:

1. **Configuration**: `_config.yml` contains all site configuration, including social media profiles, layout settings, and plugin configurations.

2. **Content Structure**:
   - `_pages/`: Main pages (about, cv, projects, publications, teaching)
   - `_posts/`: Blog posts
   - `_projects/`: Project descriptions
   - `_news/`: News/announcement items
   - `_bibliography/`: Bibliography files for publications (papers.bib, refs-en.bib, refs-pt.bib)
   - `_data/`: Structured data files (coauthors.yml, cv.yml, venues.yml)

3. **Theme Structure**:
   - `_layouts/`: Page layout templates
   - `_includes/`: Reusable components
   - `_sass/`: SCSS styling files
   - `assets/`: Static assets (images, CSS, JavaScript, PDFs)

4. **Deployment**:
   - The site is deployed to GitHub Pages
   - Docker is configured for consistent local development

## Common Tasks

### Adding a New Publication

1. Add the publication to the appropriate `.bib` file in `_bibliography/`
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