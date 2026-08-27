import datetime as dt
import random
import re

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "There are 10 kinds of people in the world: those who understand binary and those who don't.",
    "I told my computer I needed a break. It said 'no problem, I'll go to sleep.'",
]


def _safe_math(expr: str) -> str | None:
    if not re.fullmatch(r"[\d\s\+\-\*\/\(\)\.\^]+", expr):
        return None
    expr = expr.replace("^", "**")
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))
    except Exception:
        return None


def _time(_: str) -> str:
    now = dt.datetime.now()
    return f"It is {now.strftime('%H:%M')}."


def _date(_: str) -> str:
    return f"Today is {dt.date.today().strftime('%A, %B %d, %Y')}."


def _joke(_: str) -> str:
    return random.choice(JOKES)


_WORD_OPS = {
    r"\bplus\b": "+", r"\bminus\b": "-",
    r"\btimes\b": "*", r"\bmultiplied by\b": "*",
    r"\bdivided by\b": "/", r"\bover\b": "/",
}


def _math(text: str) -> str:
    normalized = text.lower()
    for pat, op in _WORD_OPS.items():
        normalized = re.sub(pat, op, normalized)
    matches = re.findall(r"[\d\s\+\-\*\/\(\)\.\^]+", normalized)
    candidate = max((m.strip() for m in matches), key=len, default="")
    if not candidate or not re.search(r"\d", candidate):
        return "I couldn't find any arithmetic in that."
    result = _safe_math(candidate)
    return f"The answer is {result}." if result is not None else "I couldn't evaluate that."


def _weather(text: str) -> str:
    m = re.search(r"weather (?:in|for) ([\w\s]+)", text.lower())
    place = m.group(1).strip().title() if m else "your area"
    return f"(demo) Right now in {place}: 22 °C, partly cloudy."


def _hello(_: str) -> str:
    return "Hello! How can I help you today?"


def _bye(_: str) -> str:
    return "Goodbye — take care."


INTENTS: list[tuple[str, callable, str]] = [
    (r"\b(hello|hi|hey)\b", _hello, "greeting"),
    (r"\b(bye|goodbye|see you)\b", _bye, "farewell"),
    (r"\bwhat time\b|\bcurrent time\b", _time, "time"),
    (r"\bwhat.+date\b|\btoday.+date\b|\bwhat day\b", _date, "date"),
    (r"\btell.+joke\b|\bmake me laugh\b", _joke, "joke"),
    (r"\bweather\b", _weather, "weather"),
    (r"(?:\bcalculate\b|\bcompute\b|\bwhat is\b|\bhow much is\b).*\d|\d\s*[\+\-\*\/]\s*\d", _math, "math"),
]


def dispatch(text: str) -> tuple[str, str]:
    lower = text.lower()
    for pattern, fn, name in INTENTS:
        if re.search(pattern, lower):
            return name, fn(text)
    return "fallback", "I didn't understand that. Try asking for the time, weather, a joke, or a calculation."
