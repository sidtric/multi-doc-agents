from agents.base import Agent
from core.client import llm, MODEL


class RAGAgent(Agent):
    name  = "RAG"
    color = "\033[96m"

    def condense(self, query, history):
        """Rewrite a follow-up ("explain the second one") into a standalone question."""
        if not history:
            return query
        convo = "\n".join(f"{m['role']}: {m['content'][:600]}" for m in history[-4:])
        response = llm.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "Rewrite the user's LATEST message as a standalone question, replacing references like "
                    "'it', 'that' or 'the second one' with the exact thing they refer to in the conversation. "
                    "Keep the meaning of the latest message, do not repeat the earlier question. "
                    "If it is already standalone, return it unchanged. Return only the question.\n\n"
                    "Examples:\n"
                    "  earlier: 'how many marks is the mid-term?'  latest: 'and the lab?'  → 'How many marks is the lab?'\n"
                    "  earlier answer lists 'SR, JK, D flip-flops'  latest: 'explain the second one'  → 'Explain the JK flip-flop.'\n"
                    "  latest: 'what is a decoder?'  → 'What is a decoder?'"
                )},
                {"role": "user", "content": f"Conversation:\n{convo}\n\nLatest message: {query}"}
            ]
        )
        standalone = response.choices[0].message.content.strip().strip('"') or query
        self.log(f"standalone query: {standalone}")
        return standalone

    def run(self, query, vectorstore):
        response = llm.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Generate 3 alternative phrasings of the query to help retrieve relevant document chunks. Return only the queries, one per line, no numbering."},
                {"role": "user", "content": query}
            ]
        )
        queries = [query] + [q.strip() for q in response.choices[0].message.content.strip().split("\n") if q.strip()][:3]
        is_syllabus_query = any(k in query.lower() for k in ("syllabus", "unit", "course content", "curriculum"))

        n_per_query = 15 if is_syllabus_query else 5
        scores = {}
        doc_map = {}
        for q in queries:
            docs, metas = vectorstore.query(q, n=n_per_query)
            for rank, (doc, meta) in enumerate(zip(docs, metas)):
                key = doc[:200]
                scores[key] = scores.get(key, 0) + 1 / (60 + rank + 1)
                doc_map[key] = (doc, meta.get("source", "unknown"))

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        limit = 40 if is_syllabus_query else 12
        result = [(doc_map[k][0], doc_map[k][1]) for k, _ in ranked[:limit]]
        self.log(f"retrieved {len(result)} chunks via RAG Fusion")
        return result
