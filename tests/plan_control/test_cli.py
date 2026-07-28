from pathlib import Path

from tools.plan_control.cli import EXIT_EMPTY, EXIT_OK, EXIT_STATE_FAILURE, main


def test_cli_discover_list_and_empty_next(tmp_path: Path, capsys) -> None:
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans" / "master-plan.md").write_text("# Master\n", encoding="utf-8")
    control = tmp_path / "control"
    assert main(["--repo", str(tmp_path), "--control-root", str(control), "discover"]) == EXIT_OK
    assert main(["--repo", str(tmp_path), "--control-root", str(control), "list", "plans"]) == EXIT_OK
    assert main(["--repo", str(tmp_path), "--control-root", str(control), "next"]) == EXIT_EMPTY
    assert "plan-v2-" in capsys.readouterr().out


def test_cli_doctor_detects_corrupt_journal(tmp_path: Path) -> None:
    control = tmp_path / "control"
    control.mkdir()
    (control / "events.jsonl").write_text("{bad\n", encoding="utf-8")
    assert (
        main(["--repo", str(tmp_path), "--control-root", str(control), "doctor"])
        == EXIT_STATE_FAILURE
    )
