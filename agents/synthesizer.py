from agents.base import Agent
from core.client import llm, MODEL


class Synthesizer(Agent):
    name  = "Synthesizer"
    color = "\033[95m"

    def _messages(self, query, context):
        ctx_text = "\n\n---\n\n".join(f"[{src}]\n{text}" for text, src in context)
        return [
            {"role": "system", "content": (
                "Answer using only the provided context. Reproduce information exactly as it appears — do not paraphrase, summarise, or add commentary.\n"
                "If the question is about a syllabus or course content:\n"
                "- SKIP sections labelled Course Objectives, Course Outcomes, or Prerequisites.\n"
                "- List ALL units found in the context in order: Unit 1, Unit 2, Unit 3, Unit 4, Unit 5 etc.\n"
                "- For each unit, reproduce the full topic list exactly as written in the document.\n"
                "- Output nothing else — no intro sentence, no commentary.\n"
                "If context is insufficient, say so."
            )},
            {"role": "user", "content": f"Context:\n{ctx_text}\n\nQuestion: {query}"}
        ]

    def run(self, query, context):
        response = llm.chat.completions.create(model=MODEL, messages=self._messages(query, context))
        self.log("answer ready")
        return response.choices[0].message.content

    def stream(self, query, context):
        self.log("streaming answer...")
        response = llm.chat.completions.create(
            model=MODEL,
            messages=self._messages(query, context),
            stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
