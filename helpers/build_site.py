#!/usr/bin/env python3
"""Build a static OSC&R website from YAML content into docs/ (GitHub Pages)."""

from __future__ import annotations

import glob
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OSCAR = os.path.join(ROOT, "content", "oscar")

TACTIC_ORDER = [
    "Reconnaissance",
    "Resource Development",
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Impact",
]

TACTIC_IDS = {
    "Reconnaissance": "TA01",
    "Resource Development": "TA02",
    "Initial Access": "TA03",
    "Execution": "TA04",
    "Persistence": "TA05",
    "Privilege Escalation": "TA06",
    "Defense Evasion": "TA07",
    "Credential Access": "TA08",
    "Lateral Movement": "TA09",
    "Collection": "TA10",
    "Exfiltration": "TA11",
    "Impact": "TA12",
}

BANNER = (
    "This is an <strong>AI-maintained continuation</strong> of OSC&amp;R, "
    "preserving the original PBOM / pbom-dev work and carrying the project forward."
)


def load_yaml_dir(rel):
    items = {}
    for path in glob.glob(os.path.join(OSCAR, rel, "*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data or "id" not in data:
            continue
        data["_path"] = path
        items[data["id"]] = data
    return items


def clean_list(values):
    if not values:
        return []
    out = []
    for v in values:
        if v in (None, "", "-"):
            continue
        out.append(v)
    return out


def md_lite(text):
    if not text:
        return ""
    text = str(text).strip()
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paras)


def refs_html(refs):
    refs = clean_list(refs)
    if not refs:
        return "<p class='muted'>None listed.</p>"
    lis = []
    for r in refs:
        if isinstance(r, dict):
            path = (r.get("reference") or r).get("path") if isinstance(r.get("reference"), dict) else r.get("path") or r.get("url")
            if path:
                lis.append(f'<li><a href="{html.escape(str(path))}" rel="noopener">{html.escape(str(path))}</a></li>')
            continue
        s = str(r)
        if s.startswith("http"):
            lis.append(f'<li><a href="{html.escape(s)}" rel="noopener">{html.escape(s)}</a></li>')
        else:
            lis.append(f"<li>{html.escape(s)}</li>")
    return "<ul class='refs'>" + "".join(lis) + "</ul>"


def page(title, body, root_prefix, crumb, extra_head=""):
    nav = f"""
    <header class="top">
      <div class="ai-banner">{BANNER}</div>
      <div class="bar">
        <a class="brand" href="{root_prefix}index.html">OSC&amp;R</a>
        <nav>
          <a href="{root_prefix}index.html">Matrix</a>
          <a href="{root_prefix}techniques/index.html">Techniques</a>
          <a href="{root_prefix}incidents/index.html">Incident mapping</a>
          <a href="{root_prefix}stories/index.html">Attack stories</a>
          <a href="{root_prefix}about.html">About</a>
        </nav>
      </div>
    </header>"""
    footer = f"""
    <footer>
      <p>OSC&amp;R (Open Software Supply Chain Attack Reference) was created by
      <a href="https://github.com/pbom-dev/OSCAR">pbom-dev</a> and its original contributors.
      This fork is AI-maintained to continue that legacy. Apache-2.0. See
      <a href="{root_prefix}about.html">About &amp; attribution</a>.</p>
    </footer>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · OSC&amp;R</title>
<link rel="stylesheet" href="{root_prefix}assets/style.css">
{extra_head}
</head>
<body>
{nav}
<main>
<p class="crumb">{crumb}</p>
{body}
</main>
{footer}
</body>
</html>
"""


CSS = """
:root {
  --bg: #10131a;
  --panel: #181c25;
  --panel-2: #1f2531;
  --ink: #eceef2;
  --muted: #9aa3b2;
  --line: #2a3140;
  --copper: #e2a24b;
  --copper-dim: #b67b2a;
  --teal: #6db3a8;
  --rose: #d46a6a;
  --chip: #2a3344;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink);
  font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif; line-height: 1.5; }
a { color: var(--copper); text-decoration: none; }
a:hover { text-decoration: underline; }
.ai-banner {
  background: #2a2114; color: #f0d9a8; font-size: 0.85rem; padding: 0.45rem 1.2rem;
  border-bottom: 1px solid #4a3a22; text-align: center;
}
.bar { display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  padding: 0.8rem 1.2rem; border-bottom: 1px solid var(--line); background: var(--panel);
  flex-wrap: wrap; }
.brand { font-weight: 700; letter-spacing: 0.08em; color: var(--ink); font-size: 1.05rem; }
.brand:hover { color: var(--copper); text-decoration: none; }
nav { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.92rem; }
nav a { color: var(--muted); }
nav a:hover { color: var(--ink); }
main { padding: 1.4rem 1.2rem 3rem; max-width: 1400px; margin: 0 auto; }
.crumb { color: var(--muted); font-size: 0.82rem; }
h1 { font-size: 1.8rem; margin: 0.2rem 0 0.6rem; font-weight: 650; }
h2 { font-size: 1.15rem; margin-top: 1.6rem; }
.lede { color: var(--muted); max-width: 70ch; }
.muted { color: var(--muted); }
.notice {
  background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--copper);
  padding: 0.9rem 1rem; margin: 1rem 0 1.4rem;
}
.stats { display: flex; gap: 0.8rem; flex-wrap: wrap; margin: 1rem 0 1.4rem; }
.stat { background: var(--panel); border: 1px solid var(--line); padding: 0.7rem 1rem; min-width: 7.5rem; }
.stat b { display: block; font-size: 1.3rem; color: var(--copper); }
.search { width: 100%; max-width: 28rem; padding: 0.55rem 0.7rem; background: var(--panel-2);
  border: 1px solid var(--line); color: var(--ink); margin: 0.6rem 0 1rem; }
.matrix-wrap { overflow-x: auto; padding-bottom: 1rem; }
.matrix { display: grid; gap: 0.45rem; align-items: start; min-width: 1100px; }
.col { background: var(--panel); border: 1px solid var(--line); min-width: 8.4rem; }
.col h3 { margin: 0; padding: 0.55rem 0.45rem; font-size: 0.72rem; letter-spacing: 0.03em;
  text-transform: uppercase; background: var(--panel-2); border-bottom: 1px solid var(--line);
  color: var(--copper); }
.col h3 span { display: block; color: var(--muted); font-weight: 500; font-size: 0.68rem; }
.tech {
  display: block; margin: 0.35rem; padding: 0.4rem 0.45rem; background: var(--chip);
  color: var(--ink); font-size: 0.75rem; line-height: 1.25; border: 1px solid transparent;
}
.tech:hover { border-color: var(--copper); text-decoration: none; }
.tech .id { color: var(--teal); font-family: ui-monospace, monospace; font-size: 0.7rem; }
.list { display: grid; gap: 0.45rem; }
.row {
  display: grid; grid-template-columns: 5.5rem 12rem 1fr; gap: 0.7rem; align-items: baseline;
  background: var(--panel); border: 1px solid var(--line); padding: 0.55rem 0.8rem;
}
.row .id { font-family: ui-monospace, monospace; color: var(--teal); }
.chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.chip { background: var(--chip); border: 1px solid var(--line); padding: 0.1rem 0.45rem;
  font-size: 0.75rem; color: var(--muted); }
.meta { color: var(--muted); font-size: 0.9rem; }
.card { background: var(--panel); border: 1px solid var(--line); padding: 1rem 1.1rem; margin: 0.8rem 0; }
.card h3 { margin-top: 0; }
.gaps { border-left: 3px solid var(--rose); }
.stage { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--teal); }
footer { border-top: 1px solid var(--line); padding: 1.2rem; color: var(--muted); font-size: 0.85rem;
  background: var(--panel); }
footer p { max-width: 1400px; margin: 0 auto; }
.refs { overflow-wrap: anywhere; }
code { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.88em; }
@media (max-width: 800px) {
  .row { grid-template-columns: 1fr; }
}
"""


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def build(dest):
    techs = load_yaml_dir("techniques")
    mits = load_yaml_dir("mitigations")
    dets = load_yaml_dir("detections")
    stories = load_yaml_dir("stories")

    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    write(os.path.join(dest, ".nojekyll"), "")
    write(os.path.join(dest, "assets", "style.css"), CSS)

    by_tactic = {t: [] for t in TACTIC_ORDER}
    for t in techs.values():
        by_tactic.setdefault(t["tactic"], []).append(t)
    for tname in by_tactic:
        by_tactic[tname].sort(key=lambda x: x["id"])

    # matrix.json for consumers
    matrix = {}
    for tname in TACTIC_ORDER:
        items = []
        for t in by_tactic.get(tname, []):
            items.append({
                "id": t["id"],
                "name": t["summary"],
                "tooltip": t["summary"],
                "tags": t.get("realm") or [],
                "url": f"techniques/{t['id']}.html",
                "description": t.get("description") or "",
            })
        matrix[tname] = {
            "items": items,
            "amount": len(items),
            "tooltip": tname,
            "tacticid": TACTIC_IDS.get(tname, ""),
        }
    write(os.path.join(dest, "data", "matrix.json"), json.dumps(matrix, indent=2) + "\n")
    write(os.path.join(ROOT, "matrix.json"), json.dumps(matrix, indent=2) + "\n")
    write(os.path.join(ROOT, "content", "website", "matrix.json"), json.dumps(matrix, indent=2) + "\n")

    # home / matrix
    cols = []
    for tname in TACTIC_ORDER:
        cells = []
        for t in by_tactic.get(tname, []):
            cells.append(
                f'<a class="tech" href="techniques/{html.escape(t["id"])}.html">'
                f'<span class="id">{html.escape(t["id"])}</span><br>{html.escape(t["summary"])}</a>'
            )
        cols.append(
            f'<div class="col"><h3>{html.escape(tname)}'
            f'<span>{TACTIC_IDS.get(tname, "")} · {len(by_tactic.get(tname, []))}</span></h3>'
            + "".join(cells) + "</div>"
        )
    n_tech, n_mit, n_det, n_story = len(techs), len(mits), len(dets), len(stories)
    home = f"""
    <h1>Open Software Supply Chain Attack Reference</h1>
    <p class="lede">OSC&amp;R is a comprehensive, systematic, and actionable way to understand
    attacker behaviors and techniques against the software supply chain — analogous to MITRE ATT&amp;CK,
    scoped to source, build, artifacts, and the CI/CD path into production.</p>
    <div class="notice">{BANNER} Original project:
    <a href="https://github.com/pbom-dev/OSCAR">github.com/pbom-dev/OSCAR</a>.
    This site is published from <a href="https://github.com/ai-anant/OSCAR">ai-anant/OSCAR</a>.</div>
    <div class="stats">
      <div class="stat"><b>{n_tech}</b> techniques</div>
      <div class="stat"><b>{n_mit}</b> mitigations</div>
      <div class="stat"><b>{n_det}</b> detections</div>
      <div class="stat"><b>{n_story}</b> mapped incidents</div>
    </div>
    <p><input class="search" id="q" placeholder="Filter techniques…"></p>
    <div class="matrix-wrap">
      <div class="matrix" style="grid-template-columns: repeat({len(TACTIC_ORDER)}, minmax(8.4rem, 1fr))">
        {''.join(cols)}
      </div>
    </div>
    <script>
    const q = document.getElementById('q');
    q.addEventListener('input', () => {{
      const v = q.value.toLowerCase();
      document.querySelectorAll('.tech').forEach(el => {{
        el.style.display = el.textContent.toLowerCase().includes(v) ? '' : 'none';
      }});
    }});
    </script>
    """
    write(os.path.join(dest, "index.html"), page("Matrix", home, "", "OSC&amp;R / Matrix"))

    # techniques index + pages
    rows = []
    for tid in sorted(techs):
        t = techs[tid]
        rows.append(
            f'<a class="row" href="{html.escape(tid)}.html">'
            f'<span class="id">{html.escape(tid)}</span>'
            f'<span>{html.escape(t["tactic"])}</span>'
            f'<span>{html.escape(t["summary"])}</span></a>'
        )
    t_index = f"""
    <h1>Techniques</h1>
    <p class="lede">{n_tech} techniques across {len(TACTIC_ORDER)} tactics.</p>
    <div class="list">{''.join(rows)}</div>
    """
    write(os.path.join(dest, "techniques", "index.html"), page("Techniques", t_index, "../", "OSC&amp;R / Techniques"))

    for tid, t in techs.items():
        m_links = []
        for mid in clean_list(t.get("mitigations")):
            name = (mits[mid].get("summary") if mid in mits else None) or mid
            m_links.append(f'<li><span class="id">{html.escape(str(mid))}</span> {html.escape(str(name))}</li>')
        d_links = []
        for did in clean_list(t.get("detections")):
            name = (dets[did].get("summary") if did in dets else None) or did
            d_links.append(f'<li><span class="id">{html.escape(str(did))}</span> {html.escape(str(name))}</li>')
        realms = " ".join(f'<span class="chip">{html.escape(r)}</span>' for r in (t.get("realm") or []))
        subs = clean_list(t.get("subTechniques") or t.get("subtechniques"))
        sub_html = ""
        if subs:
            sub_html = "<h2>Sub-techniques</h2><ul>" + "".join(
                f'<li><a href="{html.escape(s)}.html">{html.escape(s)}</a>'
                f' {html.escape(techs[s]["summary"]) if s in techs else ""}</li>'
                for s in subs
            ) + "</ul>"
        used_in = []
        for s in stories.values():
            for attack in s.get("attacks") or []:
                for tech in attack.get("techniques") or []:
                    if tech.get("techniqueID") == tid:
                        used_in.append(s)
                        break
        used_html = ""
        if used_in:
            used_html = "<h2>Seen in incidents</h2><ul>" + "".join(
                f'<li><a href="../incidents/{html.escape(s["id"])}.html">{html.escape(s["summary"])}</a></li>'
                for s in used_in
            ) + "</ul>"
        body = f"""
        <p class="meta">{html.escape(tid)} · {html.escape(t["tactic"])} · {html.escape(TACTIC_IDS.get(t["tactic"], ""))}</p>
        <h1>{html.escape(t["summary"])}</h1>
        <div class="chips">{realms}</div>
        {md_lite(t.get("description"))}
        {sub_html}
        <h2>Mitigations</h2>
        {"<ul>" + "".join(m_links) + "</ul>" if m_links else "<p class='muted'>None linked yet.</p>"}
        <h2>Detections</h2>
        {"<ul>" + "".join(d_links) + "</ul>" if d_links else "<p class='muted'>None linked yet.</p>"}
        {used_html}
        <h2>References</h2>
        {refs_html(t.get("references"))}
        """
        write(
            os.path.join(dest, "techniques", f"{tid}.html"),
            page(f"{tid} {t['summary']}", body, "../", f'OSC&amp;R / <a href="index.html">Techniques</a> / {html.escape(tid)}'),
        )

    # stories + incidents (same data; incidents page is the mapping view)
    def story_sort_key(s):
        raw = str(s.get("date") or "1970")
        m = re.match(r"(\d{4})(?:-(\d{1,2}))?", raw)
        if not m:
            return (0, 0)
        return (int(m.group(1)), int(m.group(2) or 0))

    ordered_stories = sorted(stories.values(), key=story_sort_key, reverse=True)

    def story_card(s, prefix):
        n_techs = sum(len(a.get("techniques") or []) for a in s.get("attacks") or [])
        return (
            f'<a class="card" href="{prefix}{html.escape(s["id"])}.html" style="display:block">'
            f'<div class="stage">{html.escape(str(s.get("date") or ""))}</div>'
            f'<h3>{html.escape(s["summary"])}</h3>'
            f'<p class="muted">{n_techs} mapped OSC&amp;R techniques</p></a>'
        )

    inc_index = f"""
    <h1>Incident → OSC&amp;R mapping</h1>
    <p class="lede">Real software-supply-chain incidents mapped onto OSC&amp;R techniques.
    Each entry documents attacker elements we can name today, and gaps where the framework
    was missing coverage (those gaps were added as new techniques where possible).</p>
    <div class="notice">Start here if you are reconstructing an incident: pick a case,
    read the mapped techniques, then follow links into the matrix.</div>
    {''.join(story_card(s, '') for s in ordered_stories)}
    """
    write(os.path.join(dest, "incidents", "index.html"), page("Incident mapping", inc_index, "../", "OSC&amp;R / Incident mapping"))

    st_index = f"""
    <h1>Attack stories</h1>
    <p class="lede">Narrative reconstructions of supply-chain attacks, using OSC&amp;R techniques
    as the shared language.</p>
    {''.join(story_card(s, '') for s in ordered_stories)}
    """
    write(os.path.join(dest, "stories", "index.html"), page("Attack stories", st_index, "../", "OSC&amp;R / Attack stories"))

    for s in stories.values():
        stages = []
        all_tech_rows = []
        for attack in s.get("attacks") or []:
            tech_bits = []
            for tech in attack.get("techniques") or []:
                tid = tech.get("techniqueID") or ""
                name = tech.get("techName") or (techs[tid]["summary"] if tid in techs else "")
                link = f'<a href="../techniques/{html.escape(tid)}.html">{html.escape(tid)}</a>' if tid else ""
                tech_bits.append(
                    f'<div class="card"><p class="meta">{link} · {html.escape(tech.get("tactic") or "")} · {html.escape(name)}</p>'
                    f'{md_lite(tech.get("comment"))}</div>'
                )
                all_tech_rows.append(tid)
            stages.append(
                f'<h2><span class="stage">{html.escape(attack.get("stage") or "")}</span> '
                f'{html.escape(attack.get("attack") or "")}</h2>' + "".join(tech_bits)
            )
        gaps = s.get("gaps") or []
        gap_html = ""
        if gaps:
            items = []
            for g in gaps:
                if isinstance(g, dict):
                    items.append(f"<li>{html.escape(g.get('note') or json.dumps(g))}</li>")
                else:
                    items.append(f"<li>{html.escape(str(g))}</li>")
            gap_html = '<div class="card gaps"><h3>Framework gaps noted</h3><ul>' + "".join(items) + "</ul></div>"
        unique = []
        for tid in all_tech_rows:
            if tid and tid not in unique:
                unique.append(tid)
        map_list = "<ul>" + "".join(
            f'<li><a href="../techniques/{html.escape(tid)}.html">{html.escape(tid)}</a> '
            f'{html.escape(techs[tid]["summary"]) if tid in techs else ""}</li>'
            for tid in unique
        ) + "</ul>"
        body = f"""
        <p class="meta">{html.escape(s["id"])} · {html.escape(str(s.get("date") or ""))}</p>
        <h1>{html.escape(s["summary"])}</h1>
        {md_lite(s.get("description"))}
        <h2>Mapped OSC&amp;R elements</h2>
        {map_list}
        {''.join(stages)}
        {gap_html}
        <h2>Sources</h2>
        {refs_html(s.get("links"))}
        """
        html_page = page(
            s["summary"],
            body,
            "../",
            f'OSC&amp;R / <a href="index.html">Incidents</a> / {html.escape(s["id"])}',
        )
        write(os.path.join(dest, "incidents", f"{s['id']}.html"), html_page)
        write(os.path.join(dest, "stories", f"{s['id']}.html"), html_page)

    about = f"""
    <h1>About, attribution, and stewardship</h1>
    <div class="notice"><strong>AI-maintained project.</strong> This repository and website
    are a continuation of OSC&amp;R, maintained with AI assistance, so the framework does not
    stall after the original pbom.dev site went dark.</div>
    <h2>What OSC&amp;R is</h2>
    <p>OSC&amp;R (Open Software Supply Chain Attack Reference) catalogues how adversaries
    reconnoiter, infiltrate, persist in, and profit from software supply chains — source control,
    CI/CD, artifacts, and the path into customer environments.</p>
    <h2>Original work</h2>
    <p>The framework, YAML content model, matrix, attack stories, and much of the technique
    corpus were created by the <a href="https://github.com/pbom-dev/OSCAR">pbom-dev/OSCAR</a>
    project under the Apache License 2.0. Principal original contributors include
    <strong>rubtoa</strong>, <strong>maxiozer</strong>, <strong>secvladimir</strong>,
    <strong>NaorPenso</strong>, <strong>vaq130</strong>, and <strong>6mile</strong>,
    along with other GitHub contributors. That authorship stands. This fork does not claim it.</p>
    <p>The original public site at pbom.dev is no longer the OSC&amp;R project. GitHub Pages
    for the upstream repo only rendered the README. This fork publishes the full matrix,
    technique pages, and incident mappings.</p>
    <h2>This fork</h2>
    <ul>
      <li>Hosted at <a href="https://github.com/ai-anant/OSCAR">github.com/ai-anant/OSCAR</a></li>
      <li>Website: <a href="https://ai-anant.github.io/OSCAR/">ai-anant.github.io/OSCAR</a></li>
      <li>License: Apache-2.0 (unchanged)</li>
      <li>NOTICE file records attribution required by the license</li>
    </ul>
    <p>Content updates in this fork fold in unmerged upstream pull requests (typos, YAML
    attribute names, HTML cleanup), open-issue fixes, new Impact / CI/CD techniques, a
    content linter, and incident→technique mappings for cases the original stories did not cover.</p>
    <p class="muted">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}.</p>
    """
    write(os.path.join(dest, "about.html"), page("About", about, "", "OSC&amp;R / About"))

    print(
        f"Built site → {dest} ({n_tech} techniques, {n_story} incidents)"
    )


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--dest", default=os.path.join(ROOT, "docs"))
    args = p.parse_args()
    build(args.dest)
