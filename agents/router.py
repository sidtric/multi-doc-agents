from agents.base import Agent, BOLD, RESET
from core.client import llm, MODEL


class RouterAgent(Agent):
    name  = "Router"
    color = "\033[93m"

    def run(self, query, has_docs):
        response = llm.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are a routing agent. Reply with ONLY one word: chat, rag, web, or both.\n\n"
                    f"Documents available: {has_docs}\n\n"
                    + (
                    "RULES when documents ARE available:\n"
                    "  chat — ONLY greetings and pure small talk (hi, how are you, what time is it).\n"
                    "  rag  — any subject, topic, syllabus, course, concept, or informational question — always check documents first.\n"
                    "  web  — ONLY if the user explicitly asks for news, current events, or live data.\n"
                    "  both — question needs both documents and live data.\n\n"
                    "Examples:\n"
                    "  'hi' → chat\n"
                    "  'what month is it' → chat\n"
                    "  'digital electronics syllabus' → rag\n"
                    "  'explain neural networks' → rag\n"
                    "  'latest AI news' → web\n"
                    if has_docs else
                    "RULES when NO documents are available:\n"
                    "  chat — greetings, small talk, general knowledge, math, dates.\n"
                    "  web  — current events, news, live data.\n"
                    "  rag/both — not applicable.\n"
                    )
                )},
                {"role": "user", "content": query}
            ]
        )
        decision = response.choices[0].message.content.strip().lower()
        if decision not in ("rag", "web", "both", "chat"):
            decision = "rag" if has_docs else "chat"
        # if docs loaded and query is substantive (>4 words), don't let it go to plain chat
        if has_docs and decision == "chat" and len(query.split()) > 4:
            decision = "rag"
        # always consult RAG when documents are loaded and retrieval is needed
        if has_docs and decision == "web":
            decision = "both"
        self.log(f"{BOLD}{decision}{RESET}")
        return decision
