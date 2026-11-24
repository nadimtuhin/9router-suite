import pathlib

CI = pathlib.Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"


def test_ci_runs_test_suite():
    assert "pytest" in CI.read_text(), "CI must run the pytest suite, not only py_compile"


def test_ci_covers_minimum_supported_python():
    # README promises Python 3.9+; CI must exercise it.
    assert "'3.9'" in CI.read_text()
