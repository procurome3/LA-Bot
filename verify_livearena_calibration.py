"""Tester kalibracji Live Arena V7.

Combat:
    py verify_livearena_calibration.py

Pick Leader:
    py verify_livearena_calibration.py --leader

Tester ustawia RAID na pierwszy plan, robi screenshot client-area
i nakłada TYLKO punkty potrzebne dla wybranego trybu.
"""

from pathlib import Path
import argparse
import ctypes
from ctypes import wintypes
import os
import time

from livearena_windows import enable_dpi_awareness
enable_dpi_awareness()

import cv2
import mss
import numpy as np
import pyautogui

from livearena_config import TEMPLATE_REFERENCE_SIZE
from livearena_calibration import (
    LEADER_SLOT_CENTERS,
    leader_slot_point,
    leader_confirm_point,
    skill_button_point,
)


def find_raid_window():
    user32 = ctypes.windll.user32
    matches = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True

        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True

        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip().lower()

        if title not in {"raid: shadow legends", "raid shadow legends"}:
            return True

        rect = wintypes.RECT()
        point = wintypes.POINT(0, 0)

        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return True
        if not user32.ClientToScreen(hwnd, ctypes.byref(point)):
            return True

        width = rect.right - rect.left
        height = rect.bottom - rect.top

        if width >= 500 and height >= 350:
            matches.append((hwnd, point.x, point.y, width, height))

        return True

    user32.EnumWindows(enum_proc, 0)
    return max(matches, key=lambda r: r[3] * r[4]) if matches else None


def focus(hwnd):
    user32 = ctypes.windll.user32
    try:
        user32.ShowWindow(hwnd, 9)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(0.45)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--leader",
        action="store_true",
        help="Pokaż sloty lidera i Confirm zamiast A1/A2/A3.",
    )
    args = parser.parse_args()

    found = find_raid_window()
    if found is None:
        raise SystemExit("Nie znaleziono okna Raid: Shadow Legends.")

    hwnd, left, top, width, height = found
    focus(hwnd)

    refreshed = find_raid_window()
    if refreshed:
        hwnd, left, top, width, height = refreshed

    rect = (left, top, width, height)

    ref_w, ref_h = TEMPLATE_REFERENCE_SIZE
    scale = (
        (width / float(ref_w)) +
        (height / float(ref_h))
    ) * 0.5

    print("RAID physical client:", rect)
    print("pyautogui screen:", tuple(pyautogui.size()))
    print(f"template_scale: {scale:.3f}")

    with mss.mss() as sct:
        raw = np.asarray(
            sct.grab({
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            })
        )

    frame = raw[:, :, :3].copy()

    def local(screen_point):
        return (
            int(screen_point[0] - left),
            int(screen_point[1] - top),
        )

    if args.leader:
        for index in range(len(LEADER_SLOT_CENTERS)):
            p = local(leader_slot_point(rect, index))
            cv2.circle(frame, p, 12, (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"L{index+1}",
                (p[0] + 14, p[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
            )

        confirm = local(leader_confirm_point(rect))
        cv2.circle(frame, confirm, 14, (255, 160, 0), 2)
        cv2.putText(
            frame,
            "Leader Confirm",
            (confirm[0] - 130, confirm[1] - 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 160, 0),
            2,
        )
        mode = "leader"
    else:
        for name in ("A1", "A2", "A3"):
            p = local(skill_button_point(rect, name))
            cv2.circle(frame, p, 14, (0, 255, 255), 2)
            cv2.putText(
                frame,
                name,
                (p[0] + 15, p[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
            )
        mode = "combat"

    debug = Path("./debug")
    debug.mkdir(parents=True, exist_ok=True)
    out = debug / f"livearena_calibration_{mode}.png"
    cv2.imwrite(str(out), frame)

    print("Zapisano:", out.resolve())
    if args.leader:
        print("Zielone L1-L5 powinny być na środkach kart liderów.")
        print("Niebieski punkt powinien być na środku Confirm.")
    else:
        print("Żółte A1/A2/A3 powinny być dokładnie na środkach skilli.")

    try:
        os.startfile(str(out.resolve()))
    except Exception:
        pass


if __name__ == "__main__":
    main()
