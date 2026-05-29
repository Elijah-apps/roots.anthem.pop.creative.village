import os
from dotenv import load_dotenv

from story_harvester import StoryHarvesterAgent
from cultural_texture import CulturalTextureAgent
from hook_forge import HookForgeAgent
from cinematic_arc import CinematicArcAgent
from atmosphere import AtmosphereAgent
from choral_emotion import ChoralEmotionAgent
from rythm_humanity import RhythmHumanityAgent
from organic_arrangement import OrganicArrangementAgent
from listener_memory import ListenerMemoryAgent
from hit_resonance import HitResonanceAgent
from timeless_predictor import TimelessnessPredictorAgent

load_dotenv()

class CreativeVillage:
    def __init__(self):
        self.story_harvester = StoryHarvesterAgent()
        self.cultural_texture = CulturalTextureAgent()
        self.hook_forge = HookForgeAgent()
        self.cinematic_arc = CinematicArcAgent()
        self.atmosphere = AtmosphereAgent()
        self.choral_emotion = ChoralEmotionAgent()
        self.rhythm_humanity = RhythmHumanityAgent()
        self.organic_arrangement = OrganicArrangementAgent()
        self.listener_memory = ListenerMemoryAgent()
        self.hit_resonance = HitResonanceAgent()
        self.timeless_predictor = TimelessnessPredictorAgent()

    def generate_anthem_concept(self, initial_prompt):
        print(f"--- Starting Creative Village for: {initial_prompt} ---")
        
        # 1. Story
        story_seed = self.story_harvester.generate(f"Find a story seed for: {initial_prompt}")
        print(f"\n[Story Seed]:\n{story_seed}")
        
        # 2. Cultural Texture
        textured_story = self.cultural_texture.generate(f"Add regional soul and specific imagery to this story seed: {story_seed}")
        print(f"\n[Textured Story]:\n{textured_story}")
        
        # 3. Hook
        hook = self.hook_forge.generate(f"Create a powerful hook based on this textured story: {textured_story}")
        print(f"\n[Hook]:\n{hook}")
        
        # 4. Cinematic Arc
        arc = self.cinematic_arc.generate(f"Map the emotional journey for a song with this hook: {hook}")
        print(f"\n[Cinematic Arc]:\n{arc}")
        
        # 5. Atmosphere & Rhythm
        atmosphere = self.atmosphere.generate(f"Describe the sound environment for this song: {textured_story}")
        rhythm = self.rhythm_humanity.generate(f"Suggest a human groove for this atmosphere: {atmosphere}")
        print(f"\n[Atmosphere]:\n{atmosphere}")
        print(f"\n[Rhythm]:\n{rhythm}")
        
        # 6. Choral & Arrangement
        choral = self.choral_emotion.generate(f"Plan the communal lift and choir for this hook: {hook}")
        arrangement = self.organic_arrangement.generate(f"Plan the organic production for this arc: {arc}")
        print(f"\n[Choral Emotion]:\n{choral}")
        print(f"\n[Arrangement]:\n{arrangement}")
        
        # 7. Final Polish & Evaluation
        memory = self.listener_memory.generate(f"Analyze the memorability of this hook and concept: {hook}\n{textured_story}")
        resonance = self.hit_resonance.generate(f"Evaluate the emotional resonance of this entire concept: {textured_story}\n{hook}\n{arc}")
        timelessness = self.timeless_predictor.generate(f"Predict the timelessness of this concept: {textured_story}\n{hook}")
        
        print(f"\n[Listener Memory]:\n{memory}")
        print(f"\n[Hit Resonance]:\n{resonance}")
        print(f"\n[Timelessness]:\n{timelessness}")
        
        return {
            "story": textured_story,
            "hook": hook,
            "arc": arc,
            "atmosphere": atmosphere,
            "rhythm": rhythm,
            "choral": choral,
            "arrangement": arrangement,
            "evaluation": {
                "memory": memory,
                "resonance": resonance,
                "timelessness": timelessness
            }
        }

if __name__ == "__main__":
    village = CreativeVillage()
    village.generate_anthem_concept("A song about the strength of a grandmother's hands.")
