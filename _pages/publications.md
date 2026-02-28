---
layout: page
permalink: /publications/
title: Publicações
title_en: Publications
description:
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<div class="post-header">
  <h1 class="post-title">
    <span class="lang" data-lang="pt">Publicações</span>
    <span class="lang" data-lang="en">Publications</span>
  </h1>
</div>

<div class="lang" data-lang="pt">
  <h2>Preprints</h2>
  <div class="publications">
    {% bibliography --file preprints-pt.bib %}
  </div>
  <h2>Publicações</h2>
  <div class="publications">
    {% bibliography --file refs-pt.bib %}
  </div>
</div>

<div class="lang" data-lang="en">
  <h2>Preprints</h2>
  <div class="publications">
    {% bibliography --file preprints-en.bib %}
  </div>
  <h2>Publications</h2>
  <div class="publications">
    {% bibliography --file refs-en.bib %}
  </div>
</div>
