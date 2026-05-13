import os
import subprocess
from pathlib import Path
from time import sleep

import pyautogui
import pygetwindow as gw
import pyperclip

import src.window_validator as win

NOTEPAD_TAB_STATE = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Packages"
    / "Microsoft.WindowsNotepad_8wekyb3d8bbwe"
    / "LocalState"
    / "TabState"
)


def _force_kill_notepad() -> None:
    subprocess.run(
        ["taskkill", "/F", "/IM", "Notepad.exe"],
        capture_output=True,
        check=False,
    )


def _wipe_tab_state() -> None:
    if not NOTEPAD_TAB_STATE.is_dir():
        return
    for entry in NOTEPAD_TAB_STATE.iterdir():
        if not entry.is_file():
            continue
        try:
            entry.unlink()
        except PermissionError as e:
            print(f"[notepad_driver] could not delete {entry.name}: {e}")


def launch_directly() -> None:
    subprocess.Popen(["notepad.exe"])


def ensure_clean_launch() -> None:
    _force_kill_notepad()
    win.isProcessGone("Notepad.exe", timeout_seconds=2.0)
    _wipe_tab_state()


def type_post_content(title: str, body: str):
    pyautogui.hotkey("ctrl", "a")
    content = f"Title: {title}\n\n{body}"
    pyperclip.copy(content)
    pyautogui.hotkey("ctrl", "v")


def save_as(filename: str, dir: Path):
    dir.mkdir(parents=True, exist_ok=True)
    full_path = dir / filename
    sleep(0.1)

    pyautogui.hotkey("ctrl", "shift", "s", interval=0.1)

    if not win.isAppFoused(("Save As",), timeout_seconds=5.0):
        raise RuntimeError("Save As dialog never appeared")
    sleep(0.2)

    pyperclip.copy(str(full_path))
    pyautogui.hotkey("ctrl", "v")
    sleep(0.2)
    pyautogui.press("enter")

    if win.isAppFoused(("Confirm Save As",), timeout_seconds=1.5):
        pyautogui.press("tab")
        pyautogui.press("enter")

    if not win.isAppGone(("Save As", "Confirm Save As"), timeout_seconds=2.0):
        raise RuntimeError("Save As dialog did not close")


def close(window_title: str, timeout: float = 3.0):
    for w in gw.getWindowsWithTitle(window_title):
        try:
            if w.isMinimized:
                w.restore()
            w.close()
        except Exception as e:
            print(f"[notepad_driver] WM_CLOSE failed for '{w.title}': {e}")

    if win.isProcessGone("Notepad.exe", timeout_seconds=timeout):
        return

    _force_kill_notepad()
    if not win.isProcessGone("Notepad.exe", timeout_seconds=timeout):
        raise RuntimeError("Notepad failed to close even after taskkill")
