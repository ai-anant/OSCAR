<!-- TOWNCRIER -->

# v0.2.0 (2026-09-21)

AI-maintained fork of pbom-dev/OSCAR. Website published at
https://ai-anant.github.io/OSCAR/

## Features

* GitHub Pages site: matrix, technique pages, incident → OSC&R mapping
* New techniques T0200–T0203, T0205 from upstream issues and incident gaps
* New attack stories AS7–AS15 (XZ Utils, Polyfill.io, event-stream, dependency confusion, ua-parser-js, tj-actions, Ultralytics, CircleCI, npm chalk/debug)
* Content linter (`helpers/validate_content.py`)

## Bugfixes

* Applied unmerged upstream PRs #113, #114, #115 (typos, HTML cleanup, YAML keys)
* D1171 typed as Detection (issue #108)
* T0176 wording covers disablement of controls (issue #22)
* matrix.json now records `amount` and technique `id` (issue #41)
* T0198 empty mitigation/detection lists filled

## Miscellaneous

* NOTICE and README mark this as an AI-maintained continuation with attribution to pbom-dev contributors
* CONTRIBUTING.md rewritten (issues #10, #12)

# v0.0.1 (2023-02-11)

## Features

* Initial content and structure creation for the OSC&R repository

## Bugfixes


## Miscellaneous
