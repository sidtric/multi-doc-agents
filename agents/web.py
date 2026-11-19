from agents.base import Agent
from ddgs import DDGS


class WebAgent(Agent):
    name  = "Web"
    color = "\033[92m"  # green

    def run(self, query):
        # DuckDuckGo is flaky (rate limits / empty results) — never let it break the answer
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
        except Exception as e:
            self.log(f"search failed: {e}")
            results = []
        snippets = [r["body"] for r in results]
        self.log(f"fetched {len(snippets)} results")
        return [(s, "DuckDuckGo") for s in snippets]
