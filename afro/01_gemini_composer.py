"""
01_gemini_composer.py
─────────────────────
STEP 1 OF 4 — Asset-Aware Music Brain

Sends a natural-language beat prompt + Sound Registry to Gemini.
Returns a JSON blueprint that references specific Sound IDs.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── optional .env support ───────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
except ImportError:
    sys.exit("[ERROR] google-generativeai not installed.")

# ── system instruction ───────────────────────────────────────────────────────
SYSTEM_INSTRUCTION_TEMPLATE = """
You are an expert music producer specializing in the "Master KG" style of Afro-house.
Your goal is to transform a story prompt into a multi-scene musical journey.

AVAILABLE INSTRUMENTATION (Registry):
{registry_json}

Use the "id" from the registry to specify which SoundFont or Sample set to use.

Return ONLY a valid JSON object with this exact schema:
{{
  "title": string,
  "bpm": integer,
  "key": string,
  "selected_soundfont_id": string,
  "groove_config": {{ ... }},
  "scenes": [
    {{
      "name": string,
      "energy_percent": int,
      "bars": int,
      "arrangement": {{ ... }},
      "story_beats": string (Short description of the vocal theme/narrative for this scene)
    }}
  ],
  "drums": {{ ... }}
}}
"""

def load_registry():
    path = Path("sound_registry.json")
    if not path.exists():
        return {{"soundfonts": [], "samples": []}}
    return json.loads(path.read_text())

def build_blueprint(prompt: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    registry = load_registry()
    
    instruction = SYSTEM_INSTRUCTION_TEMPLATE.format(
        registry_json=json.dumps(registry, indent=2)
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=instruction,
    )

    print(f"[Gemini] Story → \"{prompt}\"")
    response = model.generate_content(prompt)
    raw = response.text.strip()

    try:
        start_idx = raw.find('{{')
        end_idx = raw.rfind('}}')
        if start_idx != -1 and end_idx != -1:
            raw = raw[start_idx : end_idx + 1]
        blueprint = json.loads(raw)
        # Inject registry for later steps if needed
        blueprint["_registry"] = registry
    except:
        print("[ERROR] Failed to parse Gemini response.")
        raise

    return blueprint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="A soulful journey")
    parser.add_argument("--output", default="blueprint.json")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("[ERROR] No Gemini API key found.")

    blueprint = build_blueprint(args.prompt, api_key)
    Path(args.output).write_text(json.dumps(blueprint, indent=2))
    print(f"[OK] Asset-aware blueprint saved.")

if __name__ == "__main__":
    main()