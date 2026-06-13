"""
master_kg.py
────────────
The "Connective Tissue" of the Master KG Pipeline.
Provides shared state, genre-aware presets, and reaction memory.
"""

import json
from pathlib import Path
from rich.table import Table

class MasterKG:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.state = {
            "genre": "afro-house",
            "bpm": 124,
            "key": "A Minor",
            "emotion_arc": [],
            "peak_energy": 0,
            "groove_style": "straight_groove",
            "swing": 0.56,
            "note_placement": "on_grid",
            "humanization": 0.5,
            "has_climax": False,
            "energy_std": 0.0,
            "transition_density": 0.5,
            "vocal_pattern": "atmospheric",
            "lyric_tone": "neutral",
            "opt_lufs": -14.0,
            "opt_swing": 0.56,
            "opt_score": 0.0,
            "reaction_history": [],
            "parent_hex_id": None
        }

    def write(self, key, value, source=None):
        if not self.enabled: return
        self.state[key] = value
        # Source logging could be added to workflow_tracker if needed

    def read(self, key, default=None):
        if not self.enabled: return default
        return self.state.get(key, default)

    def seed_from_blueprint(self, blueprint):
        if not self.enabled: return
        bpm = blueprint.get("bpm", 124)
        self.state["bpm"] = bpm
        self.state["genre"] = "amapiano" if bpm < 118 else "afro-house"
        self.state["key"] = blueprint.get("key", "A Minor")
        
        scenes = blueprint.get("scenes", [])
        self.state["emotion_arc"] = [
            {"scene": s["name"], "energy": s.get("energy_percent", 50), "emotion": s.get("emotion", "vibe")}
            for s in scenes
        ]
        if scenes:
            self.state["peak_energy"] = max(s.get("energy_percent", 0) for s in scenes)

    def resolve_lufs(self) -> float:
        if not self.enabled: return -14.0
        # Optuna override takes precedence
        if self.state.get("opt_lufs") and self.state["opt_lufs"] != -14.0:
            return self.state["opt_lufs"]
        return -11.0 if self.state["genre"] == "amapiano" else -13.0

    def resolve_groove_config(self) -> dict:
        if not self.enabled: return {}
        # Default styles based on genre
        style = "classic_shuffle" if self.state["genre"] == "amapiano" else "straight_groove"
        placement = "behind_the_beat" if self.state["genre"] == "amapiano" else "on_grid"
        
        return {
            "shaker_style": style,
            "note_placement": placement,
            "humanization_intensity": 0.6 if self.state["genre"] == "amapiano" else 0.4
        }

    def resolve_master_dsp(self) -> dict:
        """Returns EQ and Compression presets based on genre/energy."""
        if self.state["genre"] == "amapiano":
            return {
                "target_lufs": self.resolve_lufs(),
                "low_shelf_gain": 2.5,
                "low_shelf_freq": 180,
                "high_shelf_gain": 1.5,
                "high_shelf_freq": 12000,
                "comp_ratio": 4.0
            }
        else: # afro-house
            return {
                "target_lufs": self.resolve_lufs(),
                "low_shelf_gain": 1.5,
                "low_shelf_freq": 200,
                "high_shelf_gain": 1.0,
                "high_shelf_freq": 10000,
                "comp_ratio": 3.0
            }

    def apply_reaction(self, reaction: str, prev_kg_state: dict):
        """Patches state based on user feedback words."""
        if not self.enabled: return
        self.state.update(prev_kg_state)
        self.state["parent_hex_id"] = prev_kg_state.get("hex_id")
        
        r = reaction.lower()
        if "bass" in r:
            self.state["bass_boost"] = True # Hint for agents
        if "soulful" in r:
            self.state["lyric_tone"] = "soulful"
            self.state["note_placement"] = "behind_the_beat"
        if "quiet" in r or "louder" in r:
            self.state["opt_lufs"] = self.state["opt_lufs"] + 2.0
        if "energy" in r or "euphoric" in r:
            self.state["peak_energy"] = min(100, self.state["peak_energy"] + 15)

        self.state["reaction_history"].append({
            "reaction": reaction,
            "timestamp": str(Path().cwd()) # Placeholder
        })

    def save(self, path: Path):
        if not self.enabled: return
        path.write_text(json.dumps(self.state, indent=2))

    @classmethod
    def load(cls, path: Path):
        kg = cls(enabled=True)
        if path.exists():
            kg.state = json.loads(path.read_text())
        return kg

    def summary(self) -> Table:
        table = Table(title="[bold blue]🧠 MASTER KG INTELLIGENCE SUMMARY[/bold blue]", show_header=True, header_style="bold cyan")
        table.add_column("Property", style="white")
        table.add_column("Value", style="yellow")
        
        table.add_row("Detected Genre", self.state["genre"].upper())
        table.add_row("Key / BPM", f"{self.state['key']} @ {self.state['bpm']}")
        table.add_row("Groove Profile", f"{self.state['groove_style']} ({self.state['note_placement']})")
        table.add_row("Arrangement Flow", "Climax Detected" if self.state["has_climax"] else "Atmospheric/Linear")
        table.add_row("Mastering Target", f"{self.resolve_lufs()} LUFS")
        
        if self.state["reaction_history"]:
            table.add_row("Reaction Memory", f"Refined from {self.state['parent_hex_id']}")
            
        return table
