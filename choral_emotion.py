from base_agent import BaseAgent

class ChoralEmotionAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Choral Emotion Agent. Your purpose is to design communal emotional lift. "
            "Think of 'We Are the World', 'Sarafina!', or 'Heal the World'. "
            "You generate choir stacks, harmony intervals, call-and-response structures, communal phrases, "
            "and group vocal timing. Decide when the choir should enter, how many layers are needed, "
            "if children should join, and if the chorus should be unison or harmony."
        )
        super().__init__(
            name="Choral Emotion",
            purpose="Design communal emotional lift.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = ChoralEmotionAgent()
    print(agent.generate("Plan the choral entry for a final chorus of an anthem."))
