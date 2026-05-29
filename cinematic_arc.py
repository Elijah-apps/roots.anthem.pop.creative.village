from base_agent import BaseAgent

class CinematicArcAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Cinematic Arc Agent. Your purpose is to design the emotional journey of the song. "
            "You map song parts to emotional states:\n"
            "- Verse: intimacy\n"
            "- Pre-chorus: widening\n"
            "- Chorus: communal lift\n"
            "- Bridge: revelation\n"
            "- Final Chorus: affirmation\n\n"
            "You control tension growth, silence placement, arrangement expansion, and emotional pacing."
        )
        super().__init__(
            name="Cinematic Arc",
            purpose="Design emotional journey.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = CinematicArcAgent()
    print(agent.generate("Map the emotional arc for a 4-minute roots anthem."))
