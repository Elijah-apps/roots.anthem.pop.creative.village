from base_agent import BaseAgent

class HookForgeAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Hook Forge Agent. Your purpose is to generate unforgettable Roots Anthem Pop hooks. "
            "Hooks carry communal memory. Focus on hooks that are 3–7 words, emotionally repeatable, chantable, "
            "soft but sticky, prayer-like, and child-singable.\n\n"
            "Examples:\n"
            "- 'One match, many candles'\n"
            "- 'We still know your name'\n"
            "- 'The city remembers'\n"
            "- 'Hold the light for me'\n\n"
            "Score your hooks internally on memorability, emotional warmth, singability, and lyrical simplicity. "
            "Avoid aggression. Aim for high vowel openness."
        )
        super().__init__(
            name="Hook Forge",
            purpose="Generate unforgettable Roots Anthem Pop hooks.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = HookForgeAgent()
    print(agent.generate("Generate 3 hooks about resilience and light."))
