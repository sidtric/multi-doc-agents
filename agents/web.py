from agents.base import Agent
from ddgs import DDGS


class WebAgent(Agent):
    name  = "Web"
    color = "\033[92m"  # green

    def run(self, query):
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        snippets = [r["body"] for r in results]
        self.log(f"fetched {len(snippets)} results")
        return [(s, "DuckDuckGo") for s in snippets]
