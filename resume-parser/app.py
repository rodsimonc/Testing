import io
import re
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF
import spacy
import streamlit as st

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}"
)
URL_RE = re.compile(r"https?://\S+|(?:www\.|linkedin\.com/|github\.com/)\S+", re.I)

SECTION_HEADERS = [
    "summary", "objective", "profile",
    "experience", "work experience", "employment", "professional experience",
    "education", "academic",
    "skills", "technical skills", "technologies",
    "projects", "certifications", "awards", "publications", "languages",
]

SKILL_VOCAB = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin",
    "swift", "ruby", "php", "sql", "bash", "html", "css",
    "react", "vue", "angular", "next.js", "svelte", "node.js", "express", "django",
    "flask", "fastapi", "spring", "rails", "laravel",
    "postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "linux",
    "git", "github", "gitlab", "ci/cd", "jenkins",
    "pandas", "numpy", "scikit-learn", "sklearn", "pytorch", "tensorflow", "keras",
    "spacy", "nlp", "langchain", "openai", "llm", "rag",
    "tableau", "power bi", "excel", "figma",
}


@st.cache_resource
def load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


def extract_pdf_text(data: bytes) -> str:
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text("text") for page in doc)


def extract_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def find_name(nlp_doc, text: str) -> str | None:
    for ent in nlp_doc.ents:
        if ent.label_ == "PERSON":
            candidate = ent.text.strip()
            if 2 <= len(candidate.split()) <= 4 and candidate.replace(" ", "").isalpha():
                return candidate
    for line in text.splitlines():
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and line.replace(" ", "").replace("-", "").isalpha():
            return line
    return None


def find_skills(text: str) -> list[str]:
    lower = text.lower()
    found = {s for s in SKILL_VOCAB if re.search(rf"(?<![a-z0-9+#]){re.escape(s)}(?![a-z0-9+#])", lower)}
    return sorted(found)


def split_sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current = "header"
    sections[current] = []
    for line in lines:
        stripped = line.strip().rstrip(":").lower()
        if stripped in SECTION_HEADERS:
            current = stripped
            sections.setdefault(current, [])
            continue
        sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def parse(text: str, nlp) -> dict:
    doc = nlp(text)
    emails = list(dict.fromkeys(EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys(
        p.strip() for p in PHONE_RE.findall(text)
        if sum(c.isdigit() for c in p) >= 10
        and not re.fullmatch(r"\d{4}\s*[-–]\s*\d{4}", p.strip())
    ))
    urls = list(dict.fromkeys(URL_RE.findall(text)))
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
    org_counts = [org for org, _ in Counter(orgs).most_common(10)]
    return {
        "name": find_name(doc, text),
        "emails": emails,
        "phones": phones,
        "links": urls,
        "organizations": org_counts,
        "skills": find_skills(text),
        "sections": split_sections(text),
    }


def main():
    st.set_page_config(page_title="Resume Parser", page_icon="📄")
    st.title("Resume Parser")
    st.caption("Drop a PDF or .txt resume — extracts contact info, skills, and sections.")

    nlp = load_nlp()
    uploaded = st.file_uploader("Resume", type=["pdf", "txt"])
    if not uploaded:
        st.info("Waiting for a file.")
        return

    data = uploaded.read()
    if uploaded.name.lower().endswith(".pdf"):
        text = extract_pdf_text(data)
    else:
        text = extract_txt(data)

    if not text.strip():
        st.error("Could not extract any text from that file.")
        return

    result = parse(text, nlp)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Contact")
        st.write({
            "Name": result["name"],
            "Emails": result["emails"],
            "Phones": result["phones"],
            "Links": result["links"],
        })
    with col2:
        st.subheader("Skills")
        if result["skills"]:
            st.write(", ".join(result["skills"]))
        else:
            st.write("_none matched_")
        st.subheader("Organizations")
        st.write(result["organizations"] or "_none_")

    st.subheader("Sections")
    for name, body in result["sections"].items():
        with st.expander(name.title()):
            st.text(body)

    with st.expander("Raw text"):
        st.text(text)

    st.download_button("Download JSON", data=str(result), file_name="parsed.json")


if __name__ == "__main__":
    main()
