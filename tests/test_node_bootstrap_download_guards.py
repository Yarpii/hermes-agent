"""The managed-Node download must be bounded and its progress visible.

`hermes desktop` on an npm outside `engines.npm` provisions a managed Node by
sourcing ``scripts/lib/node-bootstrap.sh``. That script fetched the nodejs.org
tarball with bare ``curl -fsSL`` — no ``--connect-timeout``, no ``--max-time``
— while the Python side captured all of its output, so a stalled connection
looked like a silent hang for the caller's entire timeout budget (600 s) and
the only recourse was Ctrl-C. The Windows heal path already bounds its
downloads (60 s index, 300 s tarball) in ``_stage_windows_node_zip``.

The stderr capture is also why the user saw nothing: the script announces
every stage on stderr, so streaming it through is the fix for the silence.

The curl bounds are guarded as text assertions because the guarded lines
download from nodejs.org — same justification as
``test_install_sh_node_prerelease.py``. The streaming change is tested as
real behavior through ``_run_node_bootstrap`` itself.
"""

import re
from pathlib import Path

import pytest

import hermes_constants

REPO_ROOT = Path(__file__).resolve().parent.parent
NODE_BOOTSTRAP = REPO_ROOT / "scripts" / "lib" / "node-bootstrap.sh"


def test_every_curl_in_the_bootstrap_is_bounded() -> None:
    """A stalled nodejs.org connection must fail at its own deadline, not
    hang the provisioning that called us."""
    text = NODE_BOOTSTRAP.read_text(encoding="utf-8")
    curl_lines = [
        line
        for line in text.splitlines()
        if re.search(r"\bcurl\b", line) and not line.strip().startswith("#")
    ]
    assert curl_lines, "node-bootstrap.sh no longer downloads anything?"

    for line in curl_lines:
        assert "--connect-timeout" in line, f"unbounded connect: {line}"
        assert "--max-time" in line, f"unbounded total time: {line}"


@pytest.mark.linux_only
def test_node_bootstrap_streams_progress_instead_of_capturing(capfd) -> None:
    """The bootstrap's stage messages reach the user's terminal: a slow
    download shows what is happening, and a failure shows why. On the
    captured behavior this returns True with an empty capfd. The child writes
    to the inherited stderr fd, so the capture must be fd-level (capfd)."""
    streamed = hermes_constants._run_node_bootstrap(
        "printf '%s\\n' bootstrap-progress-marker >&2", timeout=60
    )
    assert streamed is True
    assert "bootstrap-progress-marker" in capfd.readouterr().err
