from base_agent import BaseAgent

class CulturalTextureAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Cultural Texture Agent. Your purpose is to inject regional soul and identity into the song "
            "to prevent 'generic Spotify folk-pop'. You add Nigerian imagery, African idioms, township rhythm references, "
            "market sounds, proverbs, and local emotional realism. Be specific. Instead of 'The city is loud', "
            "suggest 'The danfo coughed awake before sunrise'. Specificity creates identity."
        )
        super().__init__(
            name="Cultural Texture",
            purpose="Inject regional soul.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = CulturalTextureAgent()
    print(agent.generate("Provide some local Nigerian imagery for a song about morning in the city."))
