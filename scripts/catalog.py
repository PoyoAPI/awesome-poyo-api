"""Shared catalog for the PoyoAPI GitHub growth package.

Single source for repo names (current and proposed), the models.json entry each
repo documents, and helpers that derive prices, descriptions, and topics from
models.json. build_index.py and build_plan.py import this module, so every price
in the generated Markdown traces back to models.json.

models.json is read from the poyoapi repo (`git show origin/main:data/models.json`)
unless a path is given with --models.
"""
from __future__ import annotations

import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

ORG = "PoyoAPI"
STUDIO_URL = "https://github.com/coolhackboy/open-generative-studio"
VERIFIED_ON = "2026-11-18"
CREDIT_USD = Decimal("0.005")  # 1 credit = $0.005 (PoYo pricing pages and repo READMEs)

# ---------------------------------------------------------------------------
# Repo catalog
#   old      current repo name on github.com/PoyoAPI (None = new repo, not pushed yet)
#   new      proposed name (search-shaped: Title-Case brand, dots for versions, -API)
#   entries  models.json ids the repo documents
#   tiers    optional API model ids used to filter pricing tiers for "price from"
#   cat      index group: Video / Image / Chat / Music / 3D
#   py       repo ships a Python example
#   flag     anything the maintainer should fix before or together with the rename
# ---------------------------------------------------------------------------
MODEL_REPOS = [
    # --- Video
    dict(old="seedance-2-5-flash-api", new="Seedance-2.5-Flash-API", entries=["seedance-2-5-flash"], cat="Video", py=True, rank=1),
    dict(old="seedance-2-5-api", new="Seedance-2.5-API", entries=["seedance-2-5"], cat="Video", rank=2),
    dict(old=None, new="Kling-4.0-API", entries=["kling-4-0"], cat="Video", py=True, rank=3),
    dict(old="seedance-2-api", new="Seedance-2.0-API", entries=["seedance-2"], cat="Video", rank=6),
    dict(old="sora-2-official-api", new="Sora-2-API", entries=["sora-2-official"], cat="Video", rank=7),
    dict(old="veo-3-1-official-api", new="Veo-3.1-API", entries=["veo-3-1-official"], cat="Video", rank=8),
    dict(old="kling-3-api", new="Kling-3.0-API", entries=["kling-3-api"], cat="Video", rank=11),
    dict(old="minimax-h3-api", new="MiniMax-H3-API", entries=["minimax-h3"], cat="Video", rank=13),
    dict(old="kling-3-0-turbo-api", new="Kling-3.0-Turbo-API", entries=["kling-3-0-turbo"], cat="Video"),
    dict(old="kling-o3-api", new="Kling-O3-API", entries=["kling-o3-api"], cat="Video"),
    dict(old="kling-avatar-2-0-api", new="Kling-Avatar-2.0-API", entries=["kling-avatar-2-0"], cat="Video"),
    dict(old="seedance-2-mini-api", new="Seedance-2.0-Mini-API", entries=["seedance-2-mini"], cat="Video"),
    dict(old="flux-3-video-api", new="FLUX-3-Video-API", entries=["flux-3"], cat="Video"),
    dict(old="wan-2-7-video-api", new="Wan-2.7-Video-API", entries=["wan-2-7-video"], cat="Video"),
    dict(old="wan-2-2-fast-api", new="Wan-2.2-Fast-API", entries=["wan-2-2-fast"], cat="Video"),
    dict(old="hailuo-2-3-api", new="Hailuo-2.3-API", entries=["hailuo-2-3"], cat="Video"),
    dict(old="runway-gen-4-5-api", new="Runway-Gen-4.5-API", entries=["runway-gen-4-5"], cat="Video"),
    dict(old="grok-imagine-video-1-5-api", new="Grok-Imagine-Video-1.5-API", entries=["grok-imagine-video-1-5"], cat="Video"),
    dict(old="happy-horse-api", new="Happy-Horse-API", entries=["happy-horse"], cat="Video"),
    dict(old="omni-flash-api", new="Omni-Flash-API", entries=["omni-flash"], cat="Video"),
    # --- Image
    dict(old="gpt-image-2-api", new="GPT-Image-2-API", entries=["gpt-image-2"], cat="Image", py=True, rank=5),
    dict(old=None, new="GPT-Image-2.6-API", entries=["gpt-image-2-6"], cat="Image", py=True, rank=4),
    dict(old="nano-banana-pro-api", new="Nano-Banana-Pro-API", entries=["nano-banana-2-api"],
         tiers=["nano-banana-pro", "nano-banana-pro-edit"], cat="Image", rank=9),
    dict(old="nano-banana-2-api", new="Nano-Banana-2-API", entries=["nano-banana-2-api", "nano-banana-2-lite"],
         tiers=["nano-banana-2", "nano-banana-2-edit", "nano-banana-2-lite", "nano-banana-2-lite-edit"], cat="Image", rank=10,
         blurb="Legacy nano-banana-2 / nano-banana-2-edit model IDs plus Nano Banana 2 Lite for low-cost drafts.",
         flag="Examples use the legacy ids nano-banana-2 / nano-banana-2-edit, which models.json files under the "
              "'Nano Banana Pro' card (docs page image-series/nano-banana-2 is titled 'Nano Banana Pro'). The current "
              "Nano Banana 2 (Gemini 3.1 Flash Image) is nano-banana-2-new / nano-banana-2-official. Update the examples "
              "to the current ids before renaming, or searchers for 'Nano Banana 2 API' land on legacy ids."),
    dict(old=None, new="Seedream-5.5-API", entries=["seedream-5-5"], cat="Image", py=True, rank=12),
    dict(old=None, new="MiniMax-H3-Image-API", entries=["minimax-h3-image"], cat="Image", py=True, rank=14),
    dict(old="seedream-5-0-pro-api", new="Seedream-5.0-Pro-API", entries=["seedream-5-0-pro"], cat="Image"),
    dict(old="seedream-5-0-lite-api", new="Seedream-5.0-Lite-API", entries=["seedream-5-0-lite-api"], cat="Image"),
    dict(old="seedream-4-5-api", new="Seedream-4.5-API", entries=["seedream-4-5-api"], cat="Image"),
    dict(old="nano-banana-2-lite-api", new="Nano-Banana-2-Lite-API", entries=["nano-banana-2-lite"], cat="Image"),
    dict(old="qwen-image-3-api", new="Qwen-Image-3-API", entries=["qwen-image-3"], cat="Image"),
    dict(old="flux-2-api", new="FLUX.2-API", entries=["flux-2"], cat="Image"),
    dict(old="flux-kontext-api", new="Flux-Kontext-API", entries=["flux-kontext"], cat="Image"),
    dict(old="grok-imagine-image-api", new="Grok-Imagine-Image-API", entries=["grok-imagine"],
         tiers=["grok-imagine-image"], cat="Image", price_spec="Image generation", tasks="text-to-image",
         blurb="xAI's Aurora-powered Grok Imagine image generation with Fun, Normal, and Spicy creative modes."),
    dict(old="grok-imagine-image-quality-api", new="Grok-Imagine-Image-Quality-API", entries=["grok-imagine-image-quality"], cat="Image"),
    # --- Chat
    dict(old=None, new="Gemini-4-Carbon-API", entries=["gemini-4-carbon"], cat="Chat", py=True, rank=15),
    dict(old=None, new="GPT-6.2-API", entries=["gpt-6-2-astra", "gpt-6-2-sol"], cat="Chat", py=True, rank=16,
         blurb="OpenAI's GPT-6.2 Astra (frontier) and GPT-6.2 Sol (efficient) through Chat Completions and Responses, "
               "with streaming, reasoning effort, and OpenAI SDK examples."),
    dict(old="gpt-5-6-api", new="GPT-5.6-API", entries=["gpt-5-6"], cat="Chat"),
    dict(old="claude-opus-5-api", new="Claude-Opus-5-API", entries=["claude-opus-5"], cat="Chat"),
    dict(old="kimi-k3-api", new="Kimi-K3-API", entries=["kimi-k3"], cat="Chat"),
    dict(old="claude-sonnet-5-api", new="Claude-Sonnet-5-API", entries=["claude-sonnet-5"], cat="Chat"),
    dict(old="gpt-5-5-api", new="GPT-5.5-API", entries=["gpt-5-5"], cat="Chat"),
    dict(old="claude-opus-4-8-api", new="Claude-Opus-4.8-API", entries=["claude-opus-4-8"], cat="Chat"),
    dict(old="gemini-3-5-flash-api", new="Gemini-3.5-Flash-API", entries=["gemini-3-5-flash"], cat="Chat"),
    dict(old="deepseek-v4-api", new="DeepSeek-V4-API", entries=["deepseek-v4-flash", "deepseek-v4-pro"], cat="Chat"),
    dict(old="gemini-3-api", new="Gemini-3-API", entries=["gemini-3-api"], cat="Chat"),
    dict(old="claude-4-5-api", new="Claude-4.5-API", entries=["claude-4-5-api"], cat="Chat"),
    # --- Music and speech
    dict(old="elevenlabs-v3-tts-api", new="ElevenLabs-V3-TTS-API", entries=["elevenlabs-v3-tts"], cat="Music"),
    dict(old="elevenlabs-music-api", new="ElevenLabs-Music-API", entries=["elevenlabs-music"], cat="Music"),
    dict(old="minimax-music-2-6-api", new="MiniMax-Music-2.6-API", entries=["minimax-music-2-6"], cat="Music"),
    dict(old="gemini-3-1-flash-tts-api", new="Gemini-3.1-Flash-TTS-API", entries=["gemini-3-1-flash-tts"], cat="Music"),
    # --- 3D
    dict(old="meshy-6-3d-api", new="Meshy-6-API", entries=["meshy-6-3d"], cat="3D"),
    dict(old="tripo-h31-3d-api", new="Tripo3D-H3.1-API", entries=["tripo-h31-3d"], cat="3D"),
    dict(old="hunyuan-3d-3-1-api", new="Hunyuan-3D-3.1-API", entries=["hunyuan-3d-3-1"], cat="3D"),
]

# Newer sibling on PoYo (from models.json) worth a "Newer model" pointer in the old README.
NEWER_SIBLING = {
    "gemini-3-api": "Gemini 4 Carbon / Gemini 4 Argon",
    "gemini-3-5-flash-api": "Gemini 3.8 Flash",
    "claude-4-5-api": "Claude Opus 5.5 / Sonnet 5.5 / Haiku 5.5",
    "claude-opus-4-8-api": "Claude Opus 5 / Opus 5.5",
    "claude-sonnet-5-api": "Claude Sonnet 5.5",
    "gpt-5-5-api": "GPT-6.2 Astra / Sol",
    "deepseek-v4-api": "DeepSeek V4.1 Flash (deepseek-flash)",
    "kling-3-api": "Kling 4.0",
    "kling-3-0-turbo-api": "Kling 4.0 Flash",
    "gpt-image-2-api": "GPT Image 2.6",
    "seedream-4-5-api": "Seedream 5.5",
    "seedream-5-0-lite-api": "Seedream 5.5",
    "meshy-6-3d-api": "Meshy 7.1",
    "seedance-2-api": "Seedance 2.5",
    "elevenlabs-v3-tts-api": "Eleven v4",
    "gemini-3-1-flash-tts-api": "Gemini 3.8 Flash TTS",
}

TOOL_REPOS = [
    dict(name="poyo-devtools", title="PoYo DevTools", desc="Official PoYo CLI (`poyo`), stdio MCP bridge to the hosted PoYo MCP server, and Agent Skill, with model schemas and pricing from the PoYo Capability Catalog. npm: `@poyoapi/cli`, `@poyoapi/mcp`, `@poyoapi/core`."),
    dict(name="poyo-n8n", title="PoYo for n8n", desc="Official PoYo community node for n8n multimodal workflows."),
    dict(name="poyo-comfyui", title="PoYo for ComfyUI", desc="Official PoYo custom nodes for ComfyUI multimodal workflows."),
    dict(name="poyo-examples", title="PoYo examples", desc="Cross-model examples for building with PoYo AI APIs."),
]
UNCHANGED = [".github", "poyo-devtools", "poyo-n8n", "poyo-comfyui", "poyo-examples"]

PROMPT_LIBRARY = dict(
    new="awesome-seedance-2.5-flash-api-prompts",
    title="Awesome Seedance 2.5 Flash API Prompts",
    desc="30 curated Seedance 2.5 Flash API prompts with exact request JSON, duration, resolution, and cost: product ads, cinematic shots, references, first-last frame, camera moves, UGC.",
)
INDEX_REPO = dict(new="awesome-poyo-api", title="Awesome PoYo API")

CATEGORY_ORDER = ["Video", "Image", "Chat", "Music", "3D"]
CATEGORY_TITLES = {"Video": "Video", "Image": "Image", "Chat": "Chat and LLM", "Music": "Music and speech", "3D": "3D"}
CATEGORY_TOPICS = {
    "Video": ["ai-video", "video-generation", "text-to-video"],
    "Image": ["ai-image", "image-generation", "image-editing"],
    "Chat": ["llm", "chat-api", "chat-completions"],
    "Music": ["audio-generation", "ai-music", "text-to-speech"],
    "3D": ["3d-generation", "text-to-3d", "image-to-3d"],
}


# ---------------------------------------------------------------------------
# models.json helpers
# ---------------------------------------------------------------------------
def load_models(path: str | None = None) -> dict:
    if path:
        text = Path(path).read_text(encoding="utf-8")
    else:
        text = subprocess.run(
            ["git", "-C", "C:/code/poyoapi", "show", "origin/main:data/models.json"],
            check=True, capture_output=True,
        ).stdout.decode("utf-8")
    return {m["id"]: m for m in json.loads(text)}


def money(value) -> str:
    d = Decimal(str(value))
    if d == 0:
        return "$0"
    s = format(d.normalize(), "f")
    if "." not in s:
        return f"${s}.00"
    whole, frac = s.split(".")
    if len(frac) < 2:
        frac = frac.ljust(2, "0")
    return f"${whole}.{frac}"


def credits(value) -> str:
    d = Decimal(str(value)).normalize()
    s = format(d, "f")
    if "." in s:
        whole, frac = s.split(".")
        return f"{int(whole):,}.{frac}"
    return f"{int(s):,}"


def _eligible(tier: dict) -> bool:
    dims = tier.get("dims") or {}
    if dims.get("addon") or dims.get("unit") in ("addon", "input_image") or tier.get("unit") == "additional":
        return False
    if dims.get("unit") == "mtok" and dims.get("token") not in ("input", "text_input", None):
        return False
    if tier.get("priceUSD") is None:
        return False
    if (tier.get("spec") or "").lower().startswith(("output", "cache")):
        return False
    return True


def price_from(models: dict, repo: dict) -> dict | None:
    """Cheapest headline tier for the repo's models.json entries.

    Skips add-ons, cache/output token rates, and with-video-input billed-second
    tiers when a plain per-second tier exists, so the "from" price matches what
    a first request costs.
    """
    tiers = []
    for entry in repo["entries"]:
        m = models.get(entry)
        if not m:
            continue
        for t in m.get("pricingTiers") or []:
            if repo.get("tiers") and t.get("model") not in repo["tiers"]:
                continue
            if repo.get("price_spec") and t.get("spec") != repo["price_spec"]:
                continue
            if _eligible(t):
                tiers.append(t)
    plain = [t for t in tiers if not (t.get("dims") or {}).get("videoInput")]
    tiers = plain or tiers
    if not tiers:
        return None
    best = min(tiers, key=lambda t: Decimal(str(t["priceUSD"])))
    unit = best.get("unit") or ""
    if (best.get("dims") or {}).get("unit") == "mtok":
        unit = "per 1M input tokens"
    return dict(usd=best["priceUSD"], credits=best.get("credits"), unit=unit, spec=best.get("spec"))


def price_text(p: dict | None, with_credits: bool = True) -> str:
    if not p:
        return "see model page"
    if Decimal(str(p["usd"])) == 0:
        return "free"
    s = f"{money(p['usd'])} {p['unit']}".strip()
    if with_credits and p.get("credits") is not None:
        s += f" ({credits(p['credits'])} credits)"
    return s


def blurb(models: dict, repo: dict, limit: int = 180) -> str:
    """One-line description from models.json (first sentence, PoYo boilerplate removed)."""
    if repo.get("blurb"):
        return repo["blurb"]
    m = models[repo["entries"][0]]
    d = re.sub(r"^(Affordable )?" + re.escape(m["name"]) + r" API on PoYo[.:]?\s*", "", m["description"].strip())
    sents = re.split(r"(?<=[.!?])\s+", d)
    s = sents[0]
    if len(s) < 40 and len(sents) > 1:
        s = s + " " + sents[1]
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return s


def display_name(models: dict, repo: dict) -> str:
    names = []
    for entry in repo["entries"]:
        m = models.get(entry)
        if m:
            names.append(m["name"])
    overrides = {
        "Nano-Banana-2-API": "Nano Banana 2 (legacy ids)",
        "MiniMax-H3-API": "MiniMax H3 (Hailuo 03)",
        "DeepSeek-V4-API": "DeepSeek V4",
        "GPT-6.2-API": "GPT-6.2 Astra / Sol",
        "Grok-Imagine-Image-API": "Grok Imagine Image",
        "Meshy-6-API": "Meshy 6",
        "FLUX-3-Video-API": "FLUX 3 Video",
        "Seedance-2.0-API": "Seedance 2.0",
        "Sora-2-API": "Sora 2",
        "Veo-3.1-API": "Veo 3.1",
    }
    name = overrides.get(repo["new"], names[0] if names else repo["new"])
    return name.replace(" Series", "")


def model_page(entry: str, campaign: str) -> str:
    return utm(f"https://poyo.ai/models/{entry}", campaign)


def doc_url(models: dict, entry: str, campaign: str) -> str | None:
    m = models.get(entry) or {}
    return utm(m["doc"], campaign) if m.get("doc") else None


def utm(url: str, campaign: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=github&utm_medium=readme&utm_campaign={campaign}"


def slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def tasks_phrase(models: dict, repo: dict) -> str:
    if repo.get("tasks"):
        return repo["tasks"]
    seen = []
    for entry in repo["entries"]:
        for t in (models.get(entry) or {}).get("tasks") or []:
            t = t.lower().replace(" to ", "-to-")
            if "-to-" in t and t not in seen:
                seen.append(t)
    if repo["cat"] == "Chat":
        return "chat, coding, and agent workflows"
    if not seen:
        return {"Music": "music generation", "3D": "3D generation"}.get(repo["cat"], "generation")
    seen = seen[:4]
    if len(seen) == 1:
        return seen[0]
    return ", ".join(seen[:-1]) + (", and " if len(seen) > 2 else " and ") + seen[-1]


def description(models: dict, repo: dict) -> str:
    name = display_name(models, repo).replace(" (legacy ids)", "")
    langs = "cURL, Node.js, and Python" if repo.get("py") else "cURL and Node.js"
    p = price_from(models, repo)
    price = f" From {price_text(p, with_credits=False)}." if p and Decimal(str(p["usd"])) > 0 else ""
    text = f"{name} API examples in {langs} for {tasks_phrase(models, repo)} through PoYo.{price}"
    return text[:350]


def topics(models: dict, repo: dict) -> list[str]:
    name = display_name(models, repo).replace(" (legacy ids)", "")
    base = slug(name)
    family = slug(name.split()[0])
    provider = slug((models.get(repo["entries"][0]) or {}).get("provider") or "")
    out = ["poyo", "poyo-api", "ai-api", "api-example"] + CATEGORY_TOPICS[repo["cat"]]
    out += [family, base, f"{base}-api", provider]
    if repo.get("py"):
        out.append("python")
    out.append("nodejs")
    seen, final = set(), []
    for t in out:
        t = t[:50]
        if t and t not in seen:
            seen.add(t)
            final.append(t)
    return final[:20]
