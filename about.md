---
layout: page
title: About
eyebrow: Who I am
subtitle: Seventeen years between a compiler and a research question.
permalink: /about/
---

I am a software engineer and researcher based in Karachi. I hold a PhD in data
mining from the Karachi Institute of Economics and Technology, and I have spent
about seventeen years building software — from small internal tools to
multinational-scale systems — mostly in healthcare, education and, more
recently, emerging technology.

Most of my industry work has been in public health informatics: tuberculosis
case-finding programmes, immunisation systems, laboratory integrations and
national data warehouses across Pakistan, the Philippines, Tajikistan, Kenya,
Zimbabwe and South Africa. The common thread is data that has to be correct,
arrive on time, and survive poor connectivity — because a missed follow-up is a
person, not a row.

My research is in **influence mining** — identifying the nodes in a complex
network whose activation spreads furthest — along with applied machine learning
in health informatics. More recently I have been working on Web3 security and
decentralised systems.

## What I'm after

My ultimate vision is to bridge the gap between academia and the industry. Too
much research never reaches a production system, and too much production code
never gets examined rigorously. I am open to collaborating with people who want
to solve social problems using software and data technologies.

{% include site-vars.html %}I am a Member of the {% for m in site_memberships %}<a href="{{ m.url }}" rel="noopener">{{ m.extra }} ({{ m.name }})</a>{% unless forloop.last %}, {% endunless %}{% endfor %}.

## Specialisations

Open-source technologies · influence mining · Urdu literature · IT and cloud
infrastructure · health informatics · decentralised applications.

## Currently

{%- assign current = site.data.companies | where: "status", "current" %}
<div>
{%- for role in current %}
  <div class="role">
    <div class="role__top">
      <h3 class="role__title">{{ role.role }}<span class="role__fte">{{ role.fte }}</span></h3>
      <span class="role__when">{{ role.start }} — {{ role.end }}</span>
    </div>
    <p class="item__sub"><span class="role__org">{{ role.org }}</span>{% if role.location %} · {{ role.location }}{% endif %}</p>
    <p class="item__body">{{ role.summary }}</p>
    {%- assign highlights = role.highlights | split: ";" %}
    {%- if highlights.size > 0 %}
    <ul>
      {%- for h in highlights %}<li>{{ h | strip }}</li>{% endfor %}
    </ul>
    {%- endif %}
  </div>
{%- endfor %}
</div>

## Before that

{%- assign past = site.data.companies | where: "status", "past" %}

<table>
  <thead><tr><th>Position</th><th>Organisation</th><th>Tenure</th></tr></thead>
  <tbody>
    {%- for r in past %}
    <tr>
      <td>{{ r.role }}</td>
      <td>{{ r.org }}{% if r.location %} <span class="faint">({{ r.location }})</span>{% endif %}</td>
      <td class="muted">{% if r.tenure %}{{ r.tenure }}{% else %}{{ r.start }} – {{ r.end }}{% endif %}</td>
    </tr>
    {%- endfor %}
  </tbody>
</table>

## Education

<ul class="items">
{%- for e in site.data.education %}
  <li class="item">
    <div class="item__head">
      <div>
        <h3 class="item__title">{{ e.degree }} — {{ e.field }}</h3>
        <p class="item__sub">{{ e.institution }}</p>
      </div>
      <span class="item__year">{{ e.year }}</span>
    </div>
  </li>
{%- endfor %}
</ul>

## Skills

<div class="skill-groups" style="margin-top:1.5rem">
{%- assign skill_groups = site.data.skills | group_by: "group" -%}
{%- for group in skill_groups %}
{%- if group.name != "core" %}
  <div class="skill-group">
    <h3>{{ group.name }}</h3>
    <ul>
      {%- for s in group.items %}
      <li>{{ s.item }}</li>
      {%- endfor %}
    </ul>
  </div>
{%- endif %}
{%- endfor %}
</div>

## Elsewhere

I write at [Vision 360](https://owaisahussain.blogspot.com/) about technology
and development, and keep a separate Urdu literary blog,
<a href="https://bazmeanjum.blogspot.com/" class="urdu">مرے جنوں کو سنبھالے اگر یہ ویرانہ</a>.

## Contact

<a href="mailto:{{ site_email }}">{{ site_email }}</a>{% if site_email_alt %} · <a href="mailto:{{ site_email_alt }}">{{ site_email_alt }}</a>{% endif %}{% if site_phone %} · {{ site_phone }}{% endif %}
{: .muted }

<p style="margin-top:2rem">
  <a class="btn btn--primary" href="mailto:{{ site_email }}">{% include icon.html name="mail" %} Get in touch</a>
  <a class="btn" href="{{ '/projects/' | relative_url }}">Projects {% include icon.html name="arrow" %}</a>
  <a class="btn" href="{{ '/research/' | relative_url }}">Research {% include icon.html name="arrow" %}</a>
</p>
