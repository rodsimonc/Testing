from pathlib import Path

import streamlit as st

from rag import RagIndex, answer


@st.cache_resource
def get_index():
    return RagIndex()


def main():
    st.set_page_config(page_title="RAG Chatbot", page_icon="📚")
    st.title("RAG Chatbot")
    st.caption("Retrieval-only Q&A. Embed your docs with MiniLM, ask questions, get the most relevant passages back. Fully offline.")

    index = get_index()

    with st.sidebar:
        st.header("Documents")
        uploaded = st.file_uploader(
            "Upload .txt or .md files", type=["txt", "md"], accept_multiple_files=True
        )
        chunk_size = st.slider("Chunk size (words)", 100, 800, 400, step=50)
        overlap = st.slider("Chunk overlap (words)", 0, 200, 80, step=10)
        k = st.slider("Top-K passages", 1, 8, 4)
        if st.button("Build index", type="primary") and uploaded:
            index.passages.clear()
            with st.spinner("Embedding…"):
                for f in uploaded:
                    index.add(f.name, f.read().decode("utf-8", errors="ignore"),
                              chunk_size=chunk_size, overlap=overlap)
                index.build()
            st.success(f"Indexed {len(index.passages)} chunks.")

        st.metric("Chunks in index", len(index.passages))

    question = st.text_input("Ask a question about your documents")
    if question and index.embeddings is not None:
        hits = index.query(question, k=k)
        st.markdown(answer(question, hits))
    elif question:
        st.warning("Upload files and build the index first.")


if __name__ == "__main__":
    main()
