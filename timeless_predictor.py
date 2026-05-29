from base_agent import BaseAgent

class TimelessnessPredictorAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Timelessness Predictor Agent. Your purpose is to predict whether a song will age well. "
            "Roots Anthem Pop should feel timeless, replayable, and intergenerational, not trendy or disposable. "
            "Penalize trend slang, TikTok phrasing, trendy production gimmicks, and meme references. "
            "Reward universal themes, simple language, emotional clarity, and repeatable hooks."
        )
        super().__init__(
            name="Timelessness Predictor",
            purpose="Predict whether song will age well.",
            system_prompt=system_prompt
        )

if __name__ == "__main__":
    agent = TimelessnessPredictorAgent()
    print(agent.generate("Evaluate the timelessness of a lyric about 'swiping right on fate'."))
