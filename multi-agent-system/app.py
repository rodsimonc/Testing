import streamlit as st

from agents import build_default_system, DEFAULT_CORPUS


def main():
    st.set_page_config(page_title="Multi-Agent System", page_icon="🤝")
    st.title("Multi-Agent System")
    st.caption("A coordinator routes each query to the best specialist agent. No LLM — the point is the orchestration pattern.")

    with st.sidebar:
        st.header("Agents")
        st.markdown("- **Calculator** — arithmetic / word problems")
        st.markdown("- **Summarizer** — condenses long text")
        st.markdown("- **Retrieval** — answers from a knowledge base")

        st.header("Knowledge base")
        st.write(f"{len(DEFAULT_CORPUS)} entries. Try: `What is FAISS?`")

    system = build_default_system()

    examples = [
        "What is 12 * (7 + 3)?",
        "What is Whisper?",
        "Summarize: Streamlit is a Python framework. It turns scripts into apps. It supports widgets and layouts. Deployment is easy.",
    ]
    st.markdown("**Try:** " + " · ".join(f"`{e}`" for e in examples))

    task = st.text_area("Task", height=100, placeholder="Ask something…")
    if st.button("Run", type="primary") and task.strip():
        result, trace = system.run(task.strip())
        st.subheader("Answer")
        st.markdown(result)

        st.subheader("Trace")
        for step in trace.steps:
            st.markdown(f"- **[{step['agent']}]** `{step['action']}` — {step['detail']}")


if __name__ == "__main__":
    main()
