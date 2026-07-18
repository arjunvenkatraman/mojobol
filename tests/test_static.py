"""Static guards for the Fix Sprint (issues #1, #2, #3).

These need no telephony and no third-party deps beyond the stdlib, so they
run in CI as the first line of defence: a stale Python 2 file, a bare
``except:``, the ``os.isfile`` typo, or a re-introduced hardcoded path all
fail here instead of on a live call.
"""
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# The engine's runtime path — must run from a fresh clone at any location.
ENGINE_FILES = [
    ROOT / "libs" / "mojobol.py",
    ROOT / "libs" / "mojoasteriskplayer.py",
    ROOT / "bin" / "mojobol-svr.py",
    ROOT / "bin" / "mojobol-svr-dev.py",
]


def all_py_files():
    for sub in ("bin", "libs", "tools", "tests"):
        yield from sorted((ROOT / sub).glob("*.py"))


def code_lines(path):
    """Yield (lineno, code-before-comment) for a file."""
    for i, line in enumerate(path.read_text().splitlines(), 1):
        yield i, line.split("#", 1)[0]


# --- T2: Python 3 port -------------------------------------------------------

def test_all_python_files_parse_under_py3():
    """A Python 2 ``print x`` statement is a SyntaxError under Py3."""
    failures = []
    for f in all_py_files():
        try:
            ast.parse(f.read_text(), filename=str(f))
        except SyntaxError as exc:
            failures.append(f"{f.relative_to(ROOT)}: {exc}")
    assert not failures, "files do not parse under Python 3:\n" + "\n".join(failures)


# --- T1: runtime bugs --------------------------------------------------------

def test_no_bare_except_in_engine_sources():
    offenders = []
    for sub in ("bin", "libs"):
        for f in sorted((ROOT / sub).glob("*.py")):
            tree = ast.parse(f.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    offenders.append(f"{f.relative_to(ROOT)}:{node.lineno}")
    assert not offenders, "bare 'except:' blocks swallow real errors: " + ", ".join(offenders)


def test_no_os_isfile_typo():
    """os.isfile does not exist; the correct call is os.path.isfile."""
    for f in sorted((ROOT / "libs").glob("*.py")):
        assert "os.isfile(" not in f.read_text(), f"os.isfile typo in {f.name}"


def test_no_pandas_dependency():
    """updatedf must not import or call the (never-imported) pandas."""
    src = (ROOT / "libs" / "mojobol.py").read_text()
    assert "import pandas" not in src
    assert "pandas." not in src


def test_stepcapture_defines_its_resources():
    """stepCapture used stepresources before assigning it (NameError)."""
    tree = ast.parse((ROOT / "libs" / "mojoasteriskplayer.py").read_text())
    func = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "stepCapture"
    )
    assigned = {
        t.id
        for node in ast.walk(func)
        if isinstance(node, ast.Assign)
        for t in node.targets
        if isinstance(t, ast.Name)
    }
    assert "stepresources" in assigned


# --- T3: no hardcoded deployment paths --------------------------------------

def test_engine_has_no_hardcoded_opt_paths():
    offenders = []
    for f in ENGINE_FILES:
        for lineno, code in code_lines(f):
            if "/opt/mojobol" in code or "/opt/voh" in code or "/opt/shwaasivr" in code:
                offenders.append(f"{f.relative_to(ROOT)}:{lineno}:{code.strip()}")
    assert not offenders, "hardcoded deployment paths in engine sources:\n" + "\n".join(offenders)


def test_setupasterisk_has_no_blanket_chmod():
    src = (ROOT / "setupasterisk.sh").read_text()
    assert "chmod a+rwx -R /opt/mojobol" not in src
