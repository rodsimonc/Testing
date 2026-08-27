import streamlit as st

from guardrails import DISCLAIMER, emergency_check
from knowledge import ALL_SYMPTOMS, match


def main():
    st.set_page_config(page_title="Medical Chatbot", page_icon="🩺")
    st.title("Medical Symptom Checker")
    st.warning(DISCLAIMER)

    st.subheader("Describe how you feel")
    freeform = st.text_area(
        "In your own words",
        placeholder="I've had a runny nose and sore throat for two days…",
        height=100,
    )

    st.subheader("Or pick from the list")
    selected = st.multiselect("Symptoms", ALL_SYMPTOMS)

    if st.button("Check", type="primary") and (freeform or selected):
        emergency = emergency_check(freeform) if freeform else None
        if emergency:
            st.error(emergency)
            st.stop()

        symptoms = set(selected)
        if freeform:
            lower = freeform.lower()
            for s in ALL_SYMPTOMS:
                if s in lower:
                    symptoms.add(s)

        if not symptoms:
            st.info("I couldn't identify specific symptoms. Please pick from the list or rephrase.")
            return

        st.write(f"**Interpreted symptoms:** {', '.join(sorted(symptoms))}")

        results = match(symptoms)
        if not results:
            st.info("No matches in the demo knowledge base. Please see a clinician.")
            return

        st.subheader("Possible conditions")
        for name, score, advice in results[:3]:
            with st.container(border=True):
                st.markdown(f"### {name.title()} — match score {score:.0%}")
                st.write(advice)

        st.info(DISCLAIMER)


if __name__ == "__main__":
    main()
