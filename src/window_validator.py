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
