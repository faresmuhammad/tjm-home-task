import subprocess
import time

import pygetwindow as gw


def isAppFoused(
    keywords: tuple[str, ...], timeout_seconds: float = 5.0, poll_interval: float = 0.2
):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        for w in gw.getAllWindows():
            title = (w.title or "").strip()
            if not title:
                continue
            if any(kw.lower() in title.lower() for kw in keywords):
                return True
        time.sleep(poll_interval)

    return False

def isAppGone(
    keywords: tuple[str, ...], timeout_seconds: float = 5.0, poll_interval: float = 0.2
):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        match = False
        for w in gw.getAllWindows():
            title = (w.title or "").strip()
            if not title:
                continue
            if any(kw.lower() in title.lower() for kw in keywords):
                match = True
                break
        if not match:
            return True
        time.sleep(poll_interval)

    return False


def isProcessRunning(exe_name: str) -> bool:
    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {exe_name}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return exe_name.lower() in result.stdout.lower()


def isProcessGone(
    exe_name: str,
    timeout_seconds: float = 5.0,
    poll_interval: float = 0.2,
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not isProcessRunning(exe_name):
            return True
        time.sleep(poll_interval)
    return False
