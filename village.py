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

class CoScientistVillage:
    """
    A collaborative AI village that works like a scientific research team.
    Phases: 1. Discovery, 2. Hypothesis (The Hook), 3. Peer Review, 4. Refinement, 5. Final Synthesis.
    """
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

    def run_session(self, initial_prompt):
        print(f"🔬 [Co-Scientist Session Start]: {initial_prompt}")
        
        # --- PHASE 1: DISCOVERY (Gathering Data) ---
        print("\n--- PHASE 1: DISCOVERY ---")
        raw_story = self.story_harvester.generate(f"Explore the emotional landscape of: {initial_prompt}")
        texture = self.cultural_texture.generate(f"Inject regional soul and specific identity into this exploration: {raw_story}")
        discovery_report = f"STORY: {raw_story}\nTEXTURE: {texture}"
        
        # --- PHASE 2: HYPOTHESIS (The Hook) ---
        print("\n--- PHASE 2: HYPOTHESIS ---")
        # Generate multiple hook candidates
        hooks_candidates = self.hook_forge.generate(f"Based on this discovery report, generate 3 distinct 'Hooks' (Hypotheses) for the anthem:\n{discovery_report}")
        print(f"[Proposed Hypotheses]:\n{hooks_candidates}")

        # --- PHASE 3: PEER REVIEW (Testing the Hypotheses) ---
        print("\n--- PHASE 3: PEER REVIEW ---")
        # The 'Scientists' critique the hooks
        critique_resonance = self.hit_resonance.generate(f"Critique these 3 hooks for emotional resonance and singability:\n{hooks_candidates}")
        critique_timeless = self.timeless_predictor.generate(f"Critique these 3 hooks for longevity and avoidance of trends:\n{hooks_candidates}")
        
        # Select the best hook based on reviews (The agents decide)
        selection_logic = f"REVIEWS:\n{critique_resonance}\n{critique_timeless}"
        best_hook = self.hook_forge.generate(f"Based on these peer reviews, select or synthesize the ONE strongest hook that satisfies all criteria:\n{selection_logic}")
        print(f"[Selected Hook]: {best_hook}")

        # --- PHASE 4: EXPERIMENTATION & REFINEMENT (The Structure) ---
        print("\n--- PHASE 4: REFINEMENT ---")
        arc = self.cinematic_arc.generate(f"Map the emotional journey for the selected hook: {best_hook}")
        atmosphere = self.atmosphere.generate(f"Refine the sonic environment to support this arc: {arc}")
        rhythm = self.rhythm_humanity.generate(f"Design a human groove that breathes with this atmosphere: {atmosphere}")
        
        # --- PHASE 5: FINAL SYNTHESIS (The Theory) ---
        print("\n--- PHASE 5: FINAL SYNTHESIS ---")
        choral = self.choral_emotion.generate(f"Synthesize the communal lift for this concept: {best_hook}\nArc: {arc}")
        arrangement = self.organic_arrangement.generate(f"Apply organic constraints to prevent overproduction of this theory: {arc}\nAtmosphere: {atmosphere}")
        
        # Final Verification
        final_memory_check = self.listener_memory.generate(f"What will the listener remember from this final 'Theory of the Song'?\nHOOK: {best_hook}\nSTORY: {texture}")

        final_report = {
            "title_hypothesis": best_hook,
            "discovery": texture,
            "emotional_architecture": arc,
            "sonic_blueprint": {
                "atmosphere": atmosphere,
                "rhythm": rhythm,
                "arrangement": arrangement
            },
            "communal_element": choral,
            "validation": final_memory_check
        }

        print("\n✅ [Co-Scientist Session Complete]: Final Song Theory established.")
        self._print_summary(final_report)
        return final_report

    def _print_summary(self, report):
        print("\n" + "="*50)
        print(f"SONG THEORY: {report['title_hypothesis']}")
        print("="*50)
        print(f"ROOTS STORY: {report['discovery'][:200]}...")
        print(f"\nEMOTIONAL ARC: {report['emotional_architecture'][:200]}...")
        print(f"\nSONIC BLUEPRINT: {report['sonic_blueprint']['rhythm']}")
        print(f"\nVALIDATION: {report['validation']}")
        print("="*50)

if __name__ == "__main__":
    village = CoScientistVillage()
    village.run_session("A song about the quiet strength of community gardens in the city.")
