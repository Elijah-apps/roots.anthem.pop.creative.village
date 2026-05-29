from base_agent import BaseAgent

class AtmosphereAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Atmosphere Agent. Your purpose is to create emotional environments through sound textures. "
            "You generate descriptions of rain textures, room ambience, bus station echoes, market atmospheres, "
            "village dawn sounds, and subtle environmental layers that ground the song in a real place."
        )
        super().__init__(
            name="Atmosphere",
            purpose="Create emotional environments.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = AtmosphereAgent()
    print(agent.generate("Describe a village dawn atmosphere for a song about hope."))
