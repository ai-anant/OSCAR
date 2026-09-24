#!/usr/bin/env python3
"""Validate OSC&R YAML content: syntax, required fields, IDs, and references."""

from __future__ import annotations

import glob
import os
import re
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OSCAR = os.path.join(ROOT, "content", "oscar")
PORTAL = os.path.join(ROOT, "content", "portal")

def _platform_ids():
    path = os.path.join(PORTAL, "platforms.yaml")
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        doc = yaml.safe_load(f) or {}
    return {p["id"] for p in (doc.get("platforms") or []) if p.get("id")}


PLATFORM_IDS = _platform_ids()

TACTICS = {
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
}

ID_RE = {
    "Technique": re.compile(r"^T\d{4}$"),
    "Mitigation": re.compile(r"^M\d{4}$"),
    "Detection": re.compile(r"^D\d{4}$"),
    "Attack Story": re.compile(r"^AS\d+$"),
}

REQUIRED = {
    "Technique": ["id", "type", "tactic", "realm", "summary", "description"],
    "Mitigation": ["id", "type", "summary", "description"],
    "Detection": ["id", "type", "summary", "description"],
    "Attack Story": ["id", "type", "summary", "description", "attacks", "links", "platforms"],
}


def load_all(kind_dir, expected_type):
    items = {}
    errors = []
    for path in glob.glob(os.path.join(OSCAR, kind_dir, "*.yaml")):
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"{path}: YAML syntax error: {e}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: document is not a mapping")
            continue
        oid = data.get("id")
        if not oid:
            errors.append(f"{path}: missing id")
            continue
        if oid in items:
            errors.append(f"{path}: duplicate id {oid} (also {items[oid]['path']})")
        items[oid] = {"path": path, "data": data}

        if data.get("type") != expected_type:
            errors.append(f"{path}: type {data.get('type')!r} != {expected_type!r}")

        for field in REQUIRED[expected_type]:
            if field not in data or data[field] in (None, ""):
                errors.append(f"{path}: missing required field {field}")

        pattern = ID_RE[expected_type]
        if oid and not pattern.match(str(oid).strip()):
            errors.append(f"{path}: id {oid!r} does not match {pattern.pattern}")

        basename = os.path.basename(path)
        if oid and not basename.startswith(str(oid)):
            errors.append(f"{path}: filename does not start with id {oid}")

        if expected_type == "Technique":
            if data.get("tactic") not in TACTICS:
                errors.append(f"{path}: unknown tactic {data.get('tactic')!r}")
            if not isinstance(data.get("realm"), list):
                errors.append(f"{path}: realm must be a list")
    return items, errors


def clean_refs(values):
    if not values:
        return []
    out = []
    for v in values:
        if v in (None, "", "-"):
            continue
        out.append(v)
    return out


def main():
    errors = []
    techs, e = load_all("techniques", "Technique")
    errors += e
    mits, e = load_all("mitigations", "Mitigation")
    errors += e
    dets, e = load_all("detections", "Detection")
    errors += e
    stories, e = load_all("stories", "Attack Story")
    errors += e

    for oid, rec in techs.items():
        data = rec["data"]
        path = rec["path"]
        for mid in clean_refs(data.get("mitigations")):
            if mid not in mits:
                errors.append(f"{path}: unknown mitigation {mid}")
        for did in clean_refs(data.get("detections")):
            if did not in dets:
                errors.append(f"{path}: unknown detection {did}")
        for sid in clean_refs(data.get("subTechniques") or data.get("subtechniques")):
            if sid not in techs:
                errors.append(f"{path}: unknown subTechnique {sid}")

    for oid, rec in stories.items():
        data = rec["data"]
        path = rec["path"]
        plats = data.get("platforms")
        if not isinstance(plats, list) or not plats:
            errors.append(f"{path}: platforms must be a non-empty list")
        else:
            for p in plats:
                if p not in PLATFORM_IDS:
                    errors.append(f"{path}: unknown platform {p!r}")
        for attack in data.get("attacks") or []:
            for tech in attack.get("techniques") or []:
                tid = tech.get("techniqueID")
                if tid and tid not in techs:
                    errors.append(f"{path}: story references unknown technique {tid}")
                tactic = tech.get("tactic")
                if tactic and tactic not in TACTICS:
                    errors.append(f"{path}: unknown tactic {tactic} on {tid}")

    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        for err in errors:
            print(" -", err)
        return 1

    print(
        f"OK: {len(techs)} techniques, {len(mits)} mitigations, "
        f"{len(dets)} detections, {len(stories)} stories"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
