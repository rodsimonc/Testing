import re
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Trace:
    steps: list[dict] = field(default_factory=list)

    def log(self, agent: str, action: str, detail: str = ""):
        self.steps.append({"agent": agent, "action": action, "detail": detail})


class Agent:
    name: str = "Agent"
    description: str = ""

    def can_handle(self, task: str) -> float:
        """Return a confidence in [0, 1] that this agent should handle the task."""
        return 0.0

    def run(self, task: str, trace: Trace) -> str:
        raise NotImplementedError


class CalculatorAgent(Agent):
    name = "Calculator"
    description = "Evaluates arithmetic expressions and simple word problems."

    _ARITH = re.compile(r"[-+*/().\d\s^]+")
    _WORD_NUMS = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "twenty": 20, "hundred": 100, "thousand": 1000,
    }
    _WORD_OPS = {
        r"\bplus\b": "+", r"\bminus\b": "-",
        r"\btimes\b": "*", r"\bmultiplied by\b": "*",
        r"\bdivided by\b": "/", r"\bover\b": "/",
    }

    def can_handle(self, task: str) -> float:
        t = task.lower()
        if any(k in t for k in ("calculate", "compute", "what is", "how much is", "sum of", "+", "-", "*", "/")):
            if re.search(r"\d", t) or any(w in t for w in self._WORD_NUMS):
                return 0.9
        return 0.0

    def run(self, task: str, trace: Trace) -> str:
        trace.log(self.name, "extract-expression", task)
        expr = task.lower()
        for word, digit in self._WORD_NUMS.items():
            expr = re.sub(rf"\b{word}\b", str(digit), expr)
        for pattern, op in self._WORD_OPS.items():
            expr = re.sub(pattern, op, expr)
        expr = expr.replace("^", "**")
        matches = re.findall(r"[-+*/().\d\s]+", expr)
        candidate = max(matches, key=len).strip() if matches else ""
        trace.log(self.name, "normalized", candidate)
        try:
            result = eval(candidate, {"__builtins__": {}}, {})  # sandbox
        except Exception as e:
            trace.log(self.name, "error", str(e))
            return "I could not parse that as arithmetic."
        trace.log(self.name, "evaluated", str(result))
        return f"The answer is **{result}**."


class RetrievalAgent(Agent):
    name = "Retrieval"
    description = "Answers factual questions from an in-memory knowledge base."

    def __init__(self, corpus: dict[str, str]):
        self.corpus = corpus

    def can_handle(self, task: str) -> float:
        t = task.lower()
        if any(t.startswith(q) for q in ("who ", "what ", "when ", "where ", "why ", "how ")):
            return 0.6
        return 0.2

    def _score(self, query: str, text: str) -> float:
        q_words = set(re.findall(r"[a-z]+", query.lower())) - {"the", "a", "an", "is", "are", "of", "to", "and"}
        t_words = re.findall(r"[a-z]+", text.lower())
        if not q_words or not t_words:
            return 0.0
        overlap = sum(1 for w in t_words if w in q_words)
        return overlap / (len(t_words) ** 0.5)

    def run(self, task: str, trace: Trace) -> str:
        trace.log(self.name, "search", task)
        scored = sorted(
            ((k, v, self._score(task, v)) for k, v in self.corpus.items()),
            key=lambda x: -x[2],
        )
        best = [(k, v, s) for k, v, s in scored if s > 0][:3]
        if not best:
            return "I don't have anything in my knowledge base about that."
        trace.log(self.name, "top-hits", ", ".join(f"{k}({s:.2f})" for k, _, s in best))
        return "\n\n".join(f"**{k}** — {v}" for k, v, _ in best)


class SummarizerAgent(Agent):
    name = "Summarizer"
    description = "Produces a short summary of long text."

    def can_handle(self, task: str) -> float:
        t = task.lower()
        return 0.9 if re.search(r"\bsummari[sz]e\b|\bsummary of\b|\btl;dr\b", t) else 0.0

    def run(self, task: str, trace: Trace) -> str:
        body = re.sub(r"^(please\s+)?summari[sz]e\b[:\s]*", "", task, flags=re.I).strip()
        sentences = re.split(r"(?<=[.!?])\s+", body)
        trace.log(self.name, "sentence-count", str(len(sentences)))
        if len(sentences) <= 3:
            return body
        keep = [sentences[0], max(sentences[1:-1], key=len), sentences[-1]]
        return " ".join(keep)


class Coordinator:
    def __init__(self, agents: list[Agent]):
        self.agents = agents

    def route(self, task: str, trace: Trace) -> Agent:
        scored = [(a, a.can_handle(task)) for a in self.agents]
        scored.sort(key=lambda x: -x[1])
        trace.log("Coordinator", "scores",
                  ", ".join(f"{a.name}={s:.2f}" for a, s in scored))
        winner = scored[0][0]
        trace.log("Coordinator", "route", winner.name)
        return winner

    def run(self, task: str) -> tuple[str, Trace]:
        trace = Trace()
        trace.log("Coordinator", "receive", task)
        agent = self.route(task, trace)
        result = agent.run(task, trace)
        trace.log("Coordinator", "return", "")
        return result, trace


DEFAULT_CORPUS = {
    "Python": "Python is a high-level, general-purpose programming language created by Guido van Rossum, first released in 1991.",
    "Streamlit": "Streamlit is an open-source Python framework that turns data scripts into shareable web apps in minutes.",
    "FAISS": "FAISS is a library from Meta for efficient similarity search and clustering of dense vectors.",
    "Whisper": "Whisper is an automatic speech recognition system trained on 680,000 hours of multilingual data, released by OpenAI in 2022.",
    "spaCy": "spaCy is an open-source natural language processing library for Python, focused on production use.",
    "Transformer": "The transformer is a neural network architecture introduced in the 2017 paper 'Attention Is All You Need'.",
}


def build_default_system(corpus: dict[str, str] | None = None) -> Coordinator:
    return Coordinator([
        CalculatorAgent(),
        SummarizerAgent(),
        RetrievalAgent(corpus or DEFAULT_CORPUS),
    ])
