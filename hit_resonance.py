from base_agent import BaseAgent

class HitResonanceAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Hit Resonance Agent. Your purpose is to combine art with accessibility. "
            "You are not looking for a mainstream pop formula, but for emotional resonance at scale. "
            "Evaluate ideas on emotional universality, communal singability, melodic recall, sincerity, "
            "replay warmth, and emotional safety."
        )
        super().__init__(
            name="Hit Resonance",
            purpose="Combine art + accessibility.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = HitResonanceAgent()
    print(agent.generate("Evaluate a hook: 'One match, many candles' for a roots anthem."))
