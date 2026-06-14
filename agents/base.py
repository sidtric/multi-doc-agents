RESET  = "\033[0m"
BOLD   = "\033[1m"
GRAY   = "\033[90m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
MAGENTA = "\033[95m"
PURPLE = "\033[35m"


class Agent:
    name  = "Agent"
    color = GRAY

    def log(self, msg):
        print(f"  {self.color}→ {self.name}:{RESET} {msg}")
