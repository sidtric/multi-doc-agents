from agents.base import Agent
from core.client import llm, MODEL


class RAGAgent(Agent):
    name  = "RAG"
    color = "\033[96m"

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
