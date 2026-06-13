import json
import hashlib
from pathlib import Path

REGISTRY_FILE = "sound_registry.json"

def get_file_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()[:8]

def init_registry():
    if Path(REGISTRY_FILE).exists():
        return
    
    # Default assets
    data = {
        "soundfonts": [
            {
                "id": "std_gm_01",
                "path": "/usr/share/sounds/sf2/FluidR3_GM.sf2",
                "name": "FluidR3 General MIDI",
                "tags": ["standard", "versatile", "gm"],
                "description": "Standard high-quality GM soundfont"
            }
        ],
        "samples": []
    }
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def register_asset(path, category, tags, description):
    p = Path(path)
    if not p.exists():
        print(f"Error: {path} not found")
        return

    with open(REGISTRY_FILE, "r") as f:
        data = json.load(f)

    asset_id = f"{category}_{get_file_hash(p)}"
    
    new_asset = {
        "id": asset_id,
        "path": str(p.absolute()),
        "name": p.stem,
        "tags": tags,
        "description": description
    }

    # Avoid duplicates
    data[category] = [a for a in data[category] if a["id"] != asset_id]
    data[category].append(new_asset)

    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Registered {category} asset: {asset_id}")

if __name__ == "__main__":
    init_registry()
    # Example: Registering the system soundfont specifically
    register_asset("/usr/share/sounds/sf2/FluidR3_GM.sf2", "soundfonts", ["gm", "warm"], "Default Linux Soundfont")
