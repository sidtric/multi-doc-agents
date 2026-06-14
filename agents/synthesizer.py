from agents.base import Agent
from core.client import llm, MODEL


class Synthesizer(Agent):
    name  = "Synthesizer"
    color = "\033[95m"

    def _messages(self, query, context):
        ctx_text = "\n\n---\n\n".join(f"[{src}]\n{text}" for text, src in context)
        return [
            {"role": "system", "content": (
                "Answer the user's question using ONLY the provided context. Never use outside knowledge.\n"
                "- If the user asks to explain or describe something: write a clear explanation using only what the context says.\n"
                "- If the user asks for a syllabus or list: reproduce the relevant content exactly as written, skipping unrelated subjects.\n"
                "- Only include content clearly relevant to the question — ignore chunks from other topics.\n"
                "- If the answer is not in the context, say: 'I could not find this in the uploaded documents.' Do not guess."
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
