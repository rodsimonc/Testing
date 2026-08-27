import streamlit as st

from reviewer import review

SEVERITY_COLOR = {"high": "🔴", "medium": "🟠", "low": "🟡"}

EXAMPLE = '''import os, json
import unused_module

def build_report(items=[]):
    password = "hunter2"
    try:
        for i in items:
            print(i)
        eval(input("cmd> "))
    except:
        pass
'''


def main():
    st.set_page_config(page_title="AI Code Reviewer", page_icon="🕵️")
    st.title("AI Code Reviewer")
    st.caption("Static analysis on Python source — mutable defaults, bare excepts, eval/exec, shell injection, hardcoded secrets, unused imports, and more. No LLM, no API.")

    code = st.text_area("Python source", value=EXAMPLE, height=280)
    if st.button("Review", type="primary") and code.strip():
        findings = review(code)
        if not findings:
            st.success("No findings.")
            return
        counts = {"high": 0, "medium": 0, "low": 0}
        for f in findings:
            counts[f.severity] += 1
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 High", counts["high"])
        c2.metric("🟠 Medium", counts["medium"])
        c3.metric("🟡 Low", counts["low"])

        for f in findings:
            with st.container(border=True):
                st.markdown(f"{SEVERITY_COLOR[f.severity]} **{f.rule}** — line {f.line}")
                st.write(f.message)


if __name__ == "__main__":
    main()
