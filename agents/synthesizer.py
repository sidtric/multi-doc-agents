from agents.base import Agent
from core.client import llm, MODEL


class Synthesizer(Agent):
    name  = "Synthesizer"
    color = "\033[95m"

    def _messages(self, query, context, history=None):
        ctx_text = "\n\n---\n\n".join(f"[{src}]\n{text}" for text, src in context)
        # last few turns so follow-ups like "explain that more" make sense
        past = [{"role": m["role"], "content": m["content"]} for m in (history or [])[-6:]]
        return [
            {"role": "system", "content": (
                "Answer the user's question using ONLY the provided context. Never use outside knowledge.\n"
                "- If the user asks to explain or describe something: write a clear explanation using only what the context says.\n"
                "- If the user asks for a syllabus or list: reproduce the relevant content exactly as written, skipping unrelated subjects.\n"
                "- Only include content clearly relevant to the question — ignore chunks from other topics.\n"
                "- Use the earlier conversation to resolve references like 'it', 'that' or 'the second one' before answering.\n"
                "- If the answer is not in the context, say: 'I could not find this in the uploaded documents.' Do not guess."
            )}
        ] + past + [
            {"role": "user", "content": f"Context:\n{ctx_text}\n\nQuestion: {query}"}
        ]

    def run(self, query, context, history=None):
        response = llm.chat.completions.create(model=MODEL, messages=self._messages(query, context, history))
        self.log("answer ready")
        return response.choices[0].message.content

    def stream(self, query, context, history=None):
        self.log("streaming answer...")
        response = llm.chat.completions.create(
            model=MODEL,
            messages=self._messages(query, context, history),
            stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
