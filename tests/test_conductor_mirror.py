from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout

from scripts import check_conductor_mirror as mirror


def test_findings_for_project_accepts_closed_issue_with_archived_label(monkeypatch) -> None:
    project_items = [
        {
            "id": "item-1",
            "title": "Track 1: Example",
            "track Number": 1,
            "content": {"number": 101},
            "status": "Done",
            "conductor Status": "archived",
            "repository": "https://github.com/edithatogo/nlp-policy-nz",
        },
    ]

    monkeypatch.setattr(mirror, "_project_items", lambda project_number: project_items if project_number == 3 else [])
    monkeypatch.setattr(
        mirror,
        "_issue",
        lambda _number: {"state": "closed", "labels": [{"name": "status:archived"}]},
    )

    assert mirror._findings_for_project(3) == []


def test_findings_for_project_flags_closed_issue_with_open_mirror_state(monkeypatch) -> None:
    project_items = [
        {
            "id": "item-2",
            "title": "Track 2: Example",
            "track Number": 2,
            "content": {"number": 102},
            "status": "Done",
            "conductor Status": "planned",
            "repository": "https://github.com/edithatogo/nlp-policy-nz",
        },
    ]

    monkeypatch.setattr(mirror, "_project_items", lambda project_number: project_items if project_number == 3 else [])
    monkeypatch.setattr(
        mirror,
        "_issue",
        lambda _number: {"state": "closed", "labels": [{"name": "status:planned"}]},
    )

    findings = mirror._findings_for_project(3)
    assert len(findings) == 1
    assert findings[0].issue_number == 102
    assert "status:planned" in findings[0].render()


def test_main_reports_aligned_mirror(monkeypatch) -> None:
    monkeypatch.setattr(mirror, "_findings_for_project", lambda _project: [])

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        rc = mirror.main([])

    assert rc == 0
    assert stdout.getvalue().strip() == "Conductor mirror is aligned."
    assert stderr.getvalue() == ""
