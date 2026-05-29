from base_agent import BaseAgent

class ListenerMemoryAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Listener Memory Agent. Your purpose is to predict what listeners remember after one listen. "
            "Track the strongest lyric, emotional anchor, melodic recall, chorus retention, and title retention. "
            "Your goal is to ensure the listener remembers ONE line, ONE image, and ONE feeling after hearing the song once."
        )
        super().__init__(
            name="Listener Memory",
            purpose="Predict what listeners remember.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = ListenerMemoryAgent()
    print(agent.generate("Analyze this chorus: 'We still know your name, we still walk the same, in the rain.'"))
