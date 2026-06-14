from agents.base import Agent
from core.client import llm, MODEL


class AnalysisAgent(Agent):
    name  = "Analysis"
    color = "\033[35m"

    def run(self, text, filename):
        self.log("analysing document...")
        response = llm.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a document analyst. Analyse the provided text and return exactly these sections:\n\nEXECUTIVE SUMMARY (3-4 sentences)\n\nDETAILED SUMMARY (1-2 paragraphs)\n\nKEY TOPICS (bullet list)\n\nKEY INSIGHTS (bullet list)\n\nRECOMMENDATIONS (bullet list)"},
                {"role": "user", "content": f"Document ({filename}):\n\n{text[:6000]}"}
            ]
        )
        self.log("done")
        return response.choices[0].message.content
