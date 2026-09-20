# OSC&R (fork)

**Open Software Supply Chain Attack Reference**

This is an **AI-maintained continuation** of [pbom-dev/OSCAR](https://github.com/pbom-dev/OSCAR). The original authors built the framework, the YAML corpus, and the early attack stories. This fork keeps that work available, applies unmerged fixes, and publishes a full website now that [pbom.dev](https://pbom.dev/) no longer hosts OSC&R.

**Live site:** https://ai-anant.github.io/OSCAR/

## What is OSC&R?

OSC&R is a comprehensive, systematic, and actionable way to understand attacker behaviors and techniques against the software supply chain — source control, CI/CD, artifacts, and the path into customer environments. It is the supply-chain counterpart to MITRE ATT&CK.

## Attribution

Original project: [pbom-dev/OSCAR](https://github.com/pbom-dev/OSCAR) (Apache-2.0).  
Principal original contributors include rubtoa, maxiozer, secvladimir, NaorPenso, vaq130, and 6mile. See [NOTICE](NOTICE).

This repository is **not** an official pbom-dev release. It is explicitly marked as AI-maintained so the lineage is obvious.

## Repository layout

- `content/oscar/techniques/` — attacker techniques (`T####`)
- `content/oscar/mitigations/` — mitigations (`M####`)
- `content/oscar/detections/` — detections (`D####`)
- `content/oscar/stories/` — incident reconstructions mapped to techniques
- `helpers/build_site.py` — static site generator (GitHub Pages)
- `helpers/validate_content.py` — YAML linter used in CI
- `docs/` — generated website (published to GitHub Pages)

## Local build

```bash
pip install -r requirements.txt
python helpers/validate_content.py
python helpers/build_site.py --dest docs
```

Open `docs/index.html`.

## What this fork changed relative to upstream

- Applied unmerged upstream PRs: typo sweep, HTML cleanup in YAML, YAML attribute names (`tooltip`, `subTechniques`, `references`)
- Fixed open issues that still applied (D1171 type, T0176 wording, matrix `amount` counts, contributing docs, content linter)
- Added missing Impact / CI/CD / reconnaissance techniques called for in upstream issues
- Added incident → OSC&R mappings (including cases upstream never documented)
- Published the matrix, technique pages, and incident mappings on GitHub Pages

## License

Apache License 2.0 — see [LICENSE](LICENSE).
