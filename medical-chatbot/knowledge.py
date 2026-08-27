"""Curated symptom → conditions knowledge base. This is illustrative, NOT medical advice."""

CONDITIONS: dict[str, dict] = {
    "common cold": {
        "symptoms": {"runny nose", "sore throat", "cough", "sneezing", "mild fever", "congestion"},
        "advice": "Rest, fluids, over-the-counter symptom relief. See a clinician if symptoms last >10 days or worsen.",
    },
    "influenza": {
        "symptoms": {"high fever", "body aches", "fatigue", "cough", "chills", "headache"},
        "advice": "Rest and fluids. Antivirals may help if started within 48 hours. See a clinician if you have shortness of breath.",
    },
    "seasonal allergies": {
        "symptoms": {"sneezing", "itchy eyes", "runny nose", "congestion", "watery eyes"},
        "advice": "Antihistamines and avoiding triggers usually help. See a clinician if symptoms disrupt daily life.",
    },
    "migraine": {
        "symptoms": {"headache", "nausea", "sensitivity to light", "sensitivity to sound", "aura"},
        "advice": "Rest in a dark, quiet room. OTC pain relief. See a clinician if headaches are new, severe, or frequent.",
    },
    "gastroenteritis": {
        "symptoms": {"nausea", "vomiting", "diarrhea", "stomach cramps", "mild fever"},
        "advice": "Hydration is critical. See a clinician if symptoms last >48h, blood is present, or dehydration signs appear.",
    },
    "dehydration": {
        "symptoms": {"thirst", "dry mouth", "fatigue", "dizziness", "dark urine", "headache"},
        "advice": "Rehydrate slowly with water or oral rehydration salts. Seek care if dizziness is severe or confusion appears.",
    },
    "sinusitis": {
        "symptoms": {"facial pain", "congestion", "runny nose", "headache", "reduced sense of smell"},
        "advice": "Saline rinses, warm compresses. See a clinician if fever is high or symptoms last >10 days.",
    },
    "strep throat": {
        "symptoms": {"sore throat", "fever", "swollen lymph nodes", "white patches on throat"},
        "advice": "Requires a clinician diagnosis — often needs antibiotics.",
    },
}


def match(symptoms: set[str]) -> list[tuple[str, float, str]]:
    """Return (condition, overlap fraction, advice) sorted by overlap desc."""
    results = []
    normalized = {s.lower().strip() for s in symptoms if s.strip()}
    for name, data in CONDITIONS.items():
        cond_symptoms = data["symptoms"]
        overlap = len(normalized & cond_symptoms)
        if overlap == 0:
            continue
        score = overlap / len(cond_symptoms)
        results.append((name, score, data["advice"]))
    results.sort(key=lambda x: -x[1])
    return results


ALL_SYMPTOMS = sorted({s for c in CONDITIONS.values() for s in c["symptoms"]})
