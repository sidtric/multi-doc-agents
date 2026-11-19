from agents.base import Agent
from ddgs import DDGS

# individual engines often return nothing (rate limits) — try each until one answers
BACKENDS = ["auto", "bing", "duckduckgo", "brave"]


class WebAgent(Agent):
    name  = "Web"
    color = "\033[92m"  # green

    def run(self, query):
        results = []
        for backend in BACKENDS:
            try:
                results = DDGS().text(query, max_results=5, backend=backend)
            except Exception as e:
                self.log(f"{backend} search failed: {e}")
                continue
            if results:
                break
        snippets = [r["body"] for r in results if r.get("body")]
        self.log(f"fetched {len(snippets)} results")
        return [(s, "Web search") for s in snippets]
