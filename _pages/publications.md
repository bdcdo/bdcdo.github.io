---
layout: page
permalink: /publications/
title: Publicações
title_en: Publications
description: Artigos, preprints e relatórios de Bruno da Cunha de Oliveira sobre judicialização da saúde, NatJus, STF e pesquisa empírica em direito, com PDFs e resumos.
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
  <div class="publications">
    {% bibliography --file preprints-pt.bib %}
  </div>
  <hr>
  <div class="publications">
    {% bibliography --file refs-pt.bib %}
  </div>
</div>

<div class="lang" data-lang="en">
  <div class="publications">
    {% bibliography --file preprints-en.bib %}
  </div>
  <hr>
  <div class="publications">
    {% bibliography --file refs-en.bib %}
  </div>
</div>
