"""Window utilities of the game (pygame)."""

import ctypes
import os
import subprocess
import sys

import pygame
from pygame._sdl2.video import Window

from ttea.log import Log

if sys.platform.startswith("win"):
    from ctypes import wintypes

    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    # Explicit types: HWND is a 64-bit pointer, the ctypes default
    # (C int) could truncate it.
    _user32.GetForegroundWindow.restype = wintypes.HWND
    _user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.c_void_p,
    ]
    _user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    _user32.AttachThreadInput.argtypes = [
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.BOOL,
    ]
    _user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    _user32.IsIconic.argtypes = [wintypes.HWND]
    _user32.keybd_event.argtypes = [
        wintypes.BYTE,
        wintypes.BYTE,
        wintypes.DWORD,
        ctypes.c_void_p,
    ]
    for _name in ("SetForegroundWindow", "BringWindowToTop", "SetFocus"):
        getattr(_user32, _name).argtypes = [wintypes.HWND]
    _kernel32.GetCurrentThreadId.restype = wintypes.DWORD

_SW_SHOW = 5
_SW_RESTORE = 9
_VK_MENU = 0x12
_KEYEVENTF_KEYUP = 0x0002


def _win_force_foreground(hwnd: int) -> bool:
    """Bring the window to the foreground on Windows.

    Parameters
    ----------
    hwnd : int
        Handle of the pygame window.

    Returns
    -------
    bool
        True if the window is in the foreground at the end.

    Notes
    -----
    Windows blocks ``SetForegroundWindow`` when another process (e.g.
    the monitoring screen that opened the game) owns the foreground.
    To get around it, the input of the current thread is attached to
    the thread of the foreground window; if that is not enough, an Alt
    press is simulated, which releases the foreground lock.
    """
    if _user32.GetForegroundWindow() == hwnd:
        return True

    if _user32.IsIconic(hwnd):
        _user32.ShowWindow(hwnd, _SW_RESTORE)
    else:
        _user32.ShowWindow(hwnd, _SW_SHOW)

    for use_alt in (False, True):
        foreground = _user32.GetForegroundWindow()
        fg_thread = _user32.GetWindowThreadProcessId(foreground, None)
        cur_thread = _kernel32.GetCurrentThreadId()

        if use_alt:
            _user32.keybd_event(_VK_MENU, 0, 0, None)
            _user32.keybd_event(_VK_MENU, 0, _KEYEVENTF_KEYUP, None)

        attached = False
        if fg_thread and fg_thread != cur_thread:
            attached = bool(
                _user32.AttachThreadInput(fg_thread, cur_thread, True)
            )
        try:
            _user32.BringWindowToTop(hwnd)
            _user32.SetForegroundWindow(hwnd)
            _user32.SetFocus(hwnd)
        finally:
            if attached:
                _user32.AttachThreadInput(fg_thread, cur_thread, False)

        if _user32.GetForegroundWindow() == hwnd:
            return True

    return False


def regain_focus() -> None:
    """Bring the pygame window back to the foreground.

    Notes
    -----
    - Windows: ``_win_force_foreground`` (user32), which works even when
      another process owns the foreground.
    - Linux: requires the ``xdotool`` tool (X11).
    - macOS: ``osascript`` brings this process to the front.

    Does nothing if pygame has no window id. Any error, or a failure to
    get the focus on Windows, does not interrupt the game: it is logged
    as a warning.
    """
    try:
        # Let SDL finish showing the window before asking for the focus.
        # Not on macOS: pumping here leaves the fullscreen window black.
        if not sys.platform.startswith("darwin"):
            pygame.event.pump()

        wm_info = pygame.display.get_wm_info()
        window_id = wm_info.get("window")
        if not window_id:
            return

        if sys.platform.startswith("win"):
            if not _win_force_foreground(window_id):
                Log.get_log().log_warning(
                    "Unable to regain focus: Windows rejected "
                    "SetForegroundWindow."
                )
        elif sys.platform.startswith("linux"):
            # Requires the xdotool tool on Linux/X11
            subprocess.run(
                ["xdotool", "windowactivate", str(window_id)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        elif sys.platform.startswith("darwin"):  # macOS
            # Make this process frontmost, then the game its key window
            # (the capture window belongs to the same process).
            apple_script = (
                'tell application "System Events" to set frontmost of '
                f"first process whose unix id is {os.getpid()} to true"
            )
            subprocess.run(
                ["osascript", "-e", apple_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            Window.from_display_module().focus()
    except Exception as error:
        # Do not stop the game, but keep the reason in the log.
        Log.get_log().log_warning(
            f"Não foi possível recuperar o foco: {error}"
        )
