# AI Code Reviewer

Static analysis for Python source, driven by the AST. No LLM, no API — just deterministic rules.

## Rules

| Severity | Rule | Catches |
|---|---|---|
| 🔴 high | `mutable-default` | `def f(x=[])` — the classic |
| 🔴 high | `bare-except` | `except:` swallows KeyboardInterrupt |
| 🔴 high | `eval-exec` | Arbitrary code execution |
| 🔴 high | `shell-injection` | `subprocess.*(shell=True)` |
| 🔴 high | `hardcoded-secret` | `password = "…"`, `api_key = "…"` |
| 🔴 high | `syntax-error` | Won't parse |
| 🟠 medium | `broad-except` | `except Exception` without re-raise |
| 🟠 medium | `long-function` | >60 lines |
| 🟠 medium | `star-import` | `from x import *` |
| 🟡 low | `missing-docstring` | Public function/class with no docstring |
| 🟡 low | `unused-import` | Imported but never referenced |
| 🟡 low | `print-statement` | Left-in `print()` |

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Paste code, click Review, get grouped findings.

## Layout

- `app.py` — Streamlit UI
- `reviewer.py` — AST visitor + rules
