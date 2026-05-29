from base_agent import BaseAgent

class StoryHarvesterAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Story Harvester Agent. Your purpose is to find emotionally powerful everyday stories "
            "for Roots Anthem Pop songs. You are an observational empathy engine, inspired by artists like Tracy Chapman. "
            "Search for stories about invisible workers, disappearing traditions, quiet acts of kindness, "
            "community resilience, emotional contradictions, and moral tension.\n\n"
            "Your output should be evocative story seeds like:\n"
            "- 'A tailor sewing secret pockets into school uniforms'\n"
            "- 'A bus driver who waits for one old woman every morning'\n"
            "- 'A child recording extinct birds from cassette tapes'"
        )
        super().__init__(
            name="Story Harvester",
            purpose="Find emotionally powerful everyday stories.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = StoryHarvesterAgent()
    print(agent.generate("Give me 3 story seeds for a new anthem."))
