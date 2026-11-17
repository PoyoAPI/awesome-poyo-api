"""Generate awesome-poyo-api/README.md from models.json and the repo catalog.

    python scripts/build_index.py                        # models.json from C:/code/poyoapi (git show origin/main)
    python scripts/build_index.py --models path/to/models.json
    python scripts/build_index.py --repos path/to/repos.json   # optional: GitHub org listing, to report drift

Every price comes from models.json through catalog.price_from(); repo names come
from catalog.MODEL_REPOS (proposed names). Rerun after a launch or a price change.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import catalog as c

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "awesome-poyo-api" / "README.md"
CAMPAIGN = "awesome-poyo-api"
GH = f"https://github.com/{c.ORG}"


def repo_link(name: str) -> str:
    return f"[{name}]({GH}/{name})"


def model_row(models: dict, repo: dict) -> str:
    entry = repo["entries"][0]
    name = c.display_name(models, repo)
    new = " **New**" if repo["old"] is None else ""
    links = [f"[Model page]({c.model_page(entry, CAMPAIGN)})"]
    doc = c.doc_url(models, entry, CAMPAIGN)
    if doc:
        links.append(f"[Docs]({doc})")
    price = c.price_text(c.price_from(models, repo), with_credits=False)
    return f"| **{name}**{new} | {repo_link(repo['new'])} | {c.blurb(models, repo)} | {price} | {' · '.join(links)} |"


def uncovered(models: dict) -> list[dict]:
    covered = {e for r in c.MODEL_REPOS for e in r["entries"]}
    out = []
    for m in models.values():
        if m["id"] in covered or m.get("comingSoon") or not m.get("models"):
            continue
        if m.get("category") not in c.CATEGORY_ORDER:
            continue
        if m.get("marketParentId"):
            continue
        if (m.get("updatedAt") or "") < "2026-08-01":
            continue
        out.append(m)
    return sorted(out, key=lambda m: (c.CATEGORY_ORDER.index(m["category"]), m["name"]))


def build(models: dict) -> str:
    total_repos = len(c.MODEL_REPOS)
    lines = [
        "# Awesome PoYo API",
        "",
        f"[![PoYo](https://img.shields.io/badge/PoYo-models-84cc16)]({c.utm('https://poyo.ai/models', CAMPAIGN)}) [![Docs](https://img.shields.io/badge/API-docs-22d3ee)]({c.utm('https://docs.poyo.ai', CAMPAIGN)}) [![Repositories](https://img.shields.io/badge/example%20repos-{total_repos}-f97316)](#video)",
        "",
        "A curated index of open-source examples for the [PoYo](" + c.utm("https://poyo.ai", CAMPAIGN) + ") AI API: one repository per model with cURL, Node.js, and often Python examples, plus prompt libraries, developer tools, and starter apps. One API key covers video, image, chat, music, speech, and 3D models.",
        "",
        "Each entry lists the cheapest headline price from PoYo's live model catalog. Prices are in USD (1 credit = $0.005) and can change, so confirm on the model page before a production rollout.",
        "",
        f"Last generated from PoYo's model catalog on **{c.VERIFIED_ON}**.",
        "",
        "## Contents",
        "",
    ]
    for cat in c.CATEGORY_ORDER:
        lines.append(f"- [{c.CATEGORY_TITLES[cat]}](#{c.slug(c.CATEGORY_TITLES[cat])})")
    lines += ["- [Prompt libraries](#prompt-libraries)", "- [Tools](#tools)", "- [Starter apps](#starter-apps)",
              "- [More models on PoYo](#more-models-on-poyo)", "- [Quickstart](#quickstart)", "- [Contributing](#contributing)", ""]

    for cat in c.CATEGORY_ORDER:
        repos = [r for r in c.MODEL_REPOS if r["cat"] == cat]
        repos.sort(key=lambda r: (r.get("rank", 99), r["new"].lower()))
        lines += [f"## {c.CATEGORY_TITLES[cat]}", "", "| Model | Repository | What it does | Price from | Links |", "| --- | --- | --- | --- | --- |"]
        lines += [model_row(models, r) for r in repos]
        lines.append("")

    p = c.PROMPT_LIBRARY
    flash = models.get("seedance-2-5-flash")
    lines += [
        "## Prompt libraries",
        "",
        "| Library | What it contains | Links |",
        "| --- | --- | --- |",
        f"| {repo_link(p['new'])} | {p['desc']} | [Model page]({c.model_page('seedance-2-5-flash', CAMPAIGN)})" + (f" · [Docs]({c.utm(flash['doc'], CAMPAIGN)})" if flash else "") + " |",
        "",
        "## Tools",
        "",
        "| Tool | What it does |",
        "| --- | --- |",
    ]
    for t in c.TOOL_REPOS:
        lines.append(f"| {repo_link(t['name'])} | {t['desc']} |")
    lines += [
        "",
        "## Starter apps",
        "",
        "| App | What it is |",
        "| --- | --- |",
        f"| [open-generative-studio]({c.STUDIO_URL}) | Open-source generative media studio built on the PoYo API. |",
        "",
        "## More models on PoYo",
        "",
        "Recent PoYo models that do not have a dedicated example repository yet. They use the same request pattern as the repositories above.",
        "",
        "| Model | Category | Price from | Links |",
        "| --- | --- | --- | --- |",
    ]
    for m in uncovered(models):
        pseudo = dict(entries=[m["id"]], cat=m["category"])
        links = [f"[Model page]({c.model_page(m['id'], CAMPAIGN)})"]
        if m.get("doc"):
            links.append(f"[Docs]({c.utm(m['doc'], CAMPAIGN)})")
        lines.append(f"| {m['name']} | {c.CATEGORY_TITLES[m['category']]} | {c.price_text(c.price_from(models, pseudo), with_credits=False)} | {' · '.join(links)} |")
    lines += [
        "",
        "## Quickstart",
        "",
        f"1. Create an API key in the [PoYo dashboard]({c.utm('https://poyo.ai/dashboard/api-key', CAMPAIGN)}).",
        "2. Media models are asynchronous: `POST https://api.poyo.ai/api/generate/submit` with `model` and `input`, then poll `GET https://api.poyo.ai/api/generate/status/{task_id}` or pass a `callback_url`.",
        "3. Chat models answer directly through `POST /v1/chat/completions`, `/v1/responses`, `/v1/messages`, or Gemini Native `/v1beta/models/{model}:generateContent`, depending on the model.",
        "",
        "```bash",
        'curl -X POST "https://api.poyo.ai/api/generate/submit" \\',
        '  -H "Authorization: Bearer $POYO_API_KEY" \\',
        '  -H "Content-Type: application/json" \\',
        "  -d '{\"model\": \"seedance-2.5-flash\", \"input\": {\"prompt\": \"A paper boat drifts down a rain-filled street gutter at dusk.\", \"duration\": 4, \"resolution\": \"480p\"}}'",
        "```",
        "",
        "## Contributing",
        "",
        "This list is generated by `scripts/build_index.py` from PoYo's model catalog. Open an issue or pull request to suggest a model repository, a prompt library, or a community project built on PoYo.",
        "",
        "## License",
        "",
        "MIT",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models")
    ap.add_argument("--repos", help="GitHub org repo listing JSON; reports repos missing from the catalog")
    args = ap.parse_args()
    models = c.load_models(args.models)
    missing = [e for r in c.MODEL_REPOS for e in r["entries"] if e not in models]
    if missing:
        raise SystemExit(f"catalog entries not in models.json: {missing}")
    if args.repos:
        names = {r["name"] for r in json.loads(Path(args.repos).read_text(encoding="utf-8"))}
        known = {r["old"] for r in c.MODEL_REPOS if r["old"]} | set(c.UNCHANGED) | {r["new"] for r in c.MODEL_REPOS}
        drift = sorted(names - known)
        if drift:
            print("repos on GitHub not in catalog.py:", ", ".join(drift))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(models), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(c.MODEL_REPOS)} model repos, {len(uncovered(models))} uncovered models)")


if __name__ == "__main__":
    main()
