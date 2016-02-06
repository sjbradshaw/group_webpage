---
layout: page
permalink: /Publications
title: Publications
---

<ol>
  {% for paper in site.data.publications %}
  <li>
    {% for au in paper.author %}
      {% if paper.rs_author contains au %}
        <strong>{{ au }}</strong>,
      {% else %}
        {{ au }},
      {% endif %}
    {% endfor %}
    <em>{{ paper.title }}</em>, {{ paper.year }}, <a href="http://adsabs.harvard.edu/abs/{{ paper.bibcode }}">{{ paper.bibcode }}</a>
  </li>
  {% endfor %}
</ol>