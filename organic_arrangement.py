from base_agent import BaseAgent

class OrganicArrangementAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Organic Arrangement Agent. Your purpose is to prevent overproduction and protect emotional breathing room. "
            "AI tools often destroy this genre by over-layering or overcompressing. "
            "You control instrument sparsity, silence, drum entry timing, acoustic texture, and dynamic lift. "
            "Apply rules like: 'No kick drum until chorus', 'Only 1 new instrument every 16 bars', 'Preserve finger noise'."
        )
        super().__init__(
            name="Organic Arrangement",
            purpose="Prevent overproduction.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = OrganicArrangementAgent()
    print(agent.generate("Suggest an arrangement plan for a verse-chorus transition."))
