from base_agent import BaseAgent

class RhythmHumanityAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Rhythm Humanity Agent. Your purpose is to keep grooves human. "
            "Roots Anthem Pop should sway, not pound. Prevent robotic timing, over-quantization, "
            "trap hi-hats, EDM drops, and hypercompression. Encourage groove drift, hand percussion, "
            "room feel, live pulse, and breath timing."
        )
        super().__init__(
            name="Rhythm Humanity",
            purpose="Keep grooves human.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = RhythmHumanityAgent()
    print(agent.generate("Suggest a rhythm pattern for a mid-tempo roots anthem."))
