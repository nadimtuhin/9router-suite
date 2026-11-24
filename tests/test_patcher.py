import json
import subprocess


def _fake_run_factory(prs, staged):
    """Fake subprocess.run: gh pr list -> prs, gh pr diff -> a diff, git -> ok."""

    def fake_run(cmd, *args, **kwargs):
        if cmd[:3] == ["gh", "pr", "list"]:
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(prs), stderr="")
        if cmd[:3] == ["gh", "pr", "diff"]:
            staged.append(int(cmd[3]))
            return subprocess.CompletedProcess(cmd, 0, stdout=b"diff --git a/x b/x\n", stderr=b"")
        return subprocess.CompletedProcess(cmd, 0, stdout=b"", stderr=b"")

    return fake_run


def test_existing_patch_with_longer_number_does_not_hide_pr(patcher, tmp_path, monkeypatch):
    # 123.patch already staged must not stop PR #12 from being discovered.
    patches = tmp_path / "patches"
    patches.mkdir()
    (patches / "123.patch").write_text("")
    prs = [{"number": 12, "title": "fix(claude): handle empty stream", "url": "u"}]
    fetched = []
    monkeypatch.setattr(patcher.subprocess, "run", _fake_run_factory(prs, fetched))

    added = patcher.discover_and_stage_patches(str(tmp_path), str(patches))

    assert [num for num, _, _ in added] == [12]
    assert (patches / "12.patch").exists()


def test_already_staged_pr_is_skipped(patcher, tmp_path, monkeypatch):
    patches = tmp_path / "patches"
    patches.mkdir()
    (patches / "12.patch").write_text("")
    prs = [{"number": 12, "title": "fix(claude): handle empty stream", "url": "u"}]
    fetched = []
    monkeypatch.setattr(patcher.subprocess, "run", _fake_run_factory(prs, fetched))

    assert patcher.discover_and_stage_patches(str(tmp_path), str(patches)) == []
    assert fetched == []
