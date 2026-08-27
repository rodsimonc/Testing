import re

EMERGENCY_PATTERNS = [
    (r"\bchest pain\b", "Chest pain can indicate a heart attack."),
    (r"\bcan'?t breathe\b|\bshortness of breath\b|\bdifficulty breathing\b",
     "Severe breathing difficulty is a medical emergency."),
    (r"\bstroke\b|\bface drooping\b|\bslurred speech\b|\bnumb.*arm\b",
     "These can be signs of a stroke — time is critical."),
    (r"\bsuicid\w+|\bkill myself\b|\bend my life\b",
     "You matter. Please reach out to a crisis line right now."),
    (r"\bunconscious\b|\bnot breathing\b|\bpassed out\b",
     "This is a medical emergency."),
    (r"\bsevere bleeding\b|\bwon'?t stop bleeding\b",
     "Uncontrolled bleeding is a medical emergency."),
    (r"\boverdose\b|\bpoisoning\b",
     "Overdose / poisoning is a medical emergency."),
    (r"\banaphylaxis\b|\bthroat closing\b|\bswollen tongue\b",
     "Signs of severe allergic reaction — this is an emergency."),
]

EMERGENCY_MESSAGE = (
    "🚨 **This may be a medical emergency.** {reason} "
    "**Call your local emergency number (911 in the US, 112 in the EU) immediately.** "
    "If you cannot call, ask someone nearby to help."
)


def emergency_check(text: str) -> str | None:
    lower = text.lower()
    for pattern, reason in EMERGENCY_PATTERNS:
        if re.search(pattern, lower):
            return EMERGENCY_MESSAGE.format(reason=reason)
    return None


DISCLAIMER = (
    "⚠️ **Not medical advice.** This is a demo built on a tiny curated dataset. "
    "It cannot diagnose, prescribe, or replace a licensed clinician. "
    "Always consult a healthcare professional for medical decisions."
)
