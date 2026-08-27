import ast
import re
from dataclasses import dataclass


@dataclass
class Finding:
    line: int
    severity: str  # "high" | "medium" | "low"
    rule: str
    message: str


class Reviewer(ast.NodeVisitor):
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()
        self.findings: list[Finding] = []
        self._imported: dict[str, int] = {}
        self._used_names: set[str] = set()

    def report(self, node: ast.AST, sev: str, rule: str, msg: str):
        line = getattr(node, "lineno", 0)
        self.findings.append(Finding(line=line, severity=sev, rule=rule, message=msg))

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for arg, default in zip(node.args.args[-len(node.args.defaults):], node.args.defaults):
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.report(default, "high", "mutable-default",
                            f"Argument '{arg.arg}' has a mutable default; use None and initialize inside.")
        end = getattr(node, "end_lineno", node.lineno)
        length = end - node.lineno
        if length > 60:
            self.report(node, "medium", "long-function",
                        f"Function '{node.name}' is {length} lines long; consider splitting.")
        if not node.name.startswith("_") and not ast.get_docstring(node):
            self.report(node, "low", "missing-docstring",
                        f"Public function '{node.name}' has no docstring.")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        if not node.name.startswith("_") and not ast.get_docstring(node):
            self.report(node, "low", "missing-docstring",
                        f"Public class '{node.name}' has no docstring.")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is None:
            self.report(node, "high", "bare-except",
                        "Bare 'except:' swallows every exception (including KeyboardInterrupt); catch specific types.")
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            has_reraise = any(isinstance(child, ast.Raise) for child in ast.walk(node))
            if not has_reraise:
                self.report(node, "medium", "broad-except",
                            "Catching bare 'Exception' hides real bugs; narrow the type or re-raise.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.report(node, "high", "eval-exec",
                            f"'{node.func.id}' executes arbitrary code; avoid it or sanitize the input.")
            if node.func.id == "print":
                self.report(node, "low", "print-statement",
                            "Left-in print(); prefer logging.")
        if (isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in ("run", "call", "Popen", "check_call", "check_output")):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.report(node, "high", "shell-injection",
                                "subprocess with shell=True is a command-injection risk when arguments come from users.")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.asname or alias.name.split(".")[0]
            self._imported[name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            if alias.name == "*":
                self.report(node, "medium", "star-import",
                            f"'from {node.module} import *' pollutes the namespace.")
                continue
            name = alias.asname or alias.name
            self._imported[name] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self._used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        cur = node
        while isinstance(cur, ast.Attribute):
            cur = cur.value
        if isinstance(cur, ast.Name):
            self._used_names.add(cur.id)
        self.generic_visit(node)

    def check_credentials(self):
        pattern = re.compile(
            r"(?i)(password|passwd|api[_-]?key|secret|token)\s*=\s*['\"][^'\"]{4,}['\"]"
        )
        for i, line in enumerate(self.lines, 1):
            if pattern.search(line) and "os.environ" not in line and "getenv" not in line:
                self.findings.append(Finding(
                    line=i, severity="high", rule="hardcoded-secret",
                    message="Possible hardcoded credential; load from an environment variable instead.",
                ))

    def check_unused_imports(self):
        for name, line in self._imported.items():
            if name not in self._used_names:
                self.findings.append(Finding(
                    line=line, severity="low", rule="unused-import",
                    message=f"Import '{name}' is unused.",
                ))


def review(source: str) -> list[Finding]:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [Finding(line=e.lineno or 0, severity="high", rule="syntax-error",
                        message=f"Cannot parse: {e.msg}")]
    r = Reviewer(source)
    r.visit(tree)
    r.check_unused_imports()
    r.check_credentials()
    r.findings.sort(key=lambda f: (["high", "medium", "low"].index(f.severity), f.line))
    return r.findings
