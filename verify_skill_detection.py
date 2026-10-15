"""Diagnostyka paska skilli V8.

Uruchom PODCZAS WŁASNEJ TURY:
    py verify_skill_detection.py

Nie zakłada pozycji A1/A2/A3/A4.
Pokazuje:
- CYAN S1/S2/... = wykryte okrągłe sloty od lewej do prawej,
- ZIELONY box = faktycznie dopasowany template skill_*.PNG,
- ostatni slot z "P" pozostaje pasywką i nie jest używany jako fallback.

Nic nie klika.
"""

from pathlib import Path
import ctypes
from ctypes import wintypes
import os
import time

from livearena_windows import enable_dpi_awareness
enable_dpi_awareness()

import cv2
import mss
import numpy as np

from livearena_config import (
    SKILL_PLAN,
    GLOBAL_SKILL_PLAN,
    TEMPLATE_REFERENCE_SIZE,
)
from livearena_vision import VisionEngine
from livearena_config import template_roi_for


def find_raid_window():
    user32 = ctypes.windll.user32
    matches = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True

        n = user32.GetWindowTextLengthW(hwnd)
        if n <= 0:
            return True

        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)

        if buf.value.strip().lower() not in {
            "raid: shadow legends",
            "raid shadow legends",
        }:
            return True

        rect = wintypes.RECT()
        pt = wintypes.POINT(0, 0)

        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return True
        if not user32.ClientToScreen(hwnd, ctypes.byref(pt)):
            return True

        w = rect.right - rect.left
        h = rect.bottom - rect.top

        if w >= 500 and h >= 350:
            matches.append((hwnd, pt.x, pt.y, w, h))

        return True

    user32.EnumWindows(enum_proc, 0)
    return max(matches, key=lambda x: x[3] * x[4]) if matches else None


def main():
    found = find_raid_window()
    if not found:
        raise SystemExit("Nie znaleziono Raid: Shadow Legends.")

    hwnd, left, top, width, height = found

    try:
        ctypes.windll.user32.ShowWindow(hwnd, 9)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass

    time.sleep(0.4)

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

    # Dolny pasek.
    y1 = round(615 * height / 793)
    x1 = round(390 * width / 1020)
    crop = frame[y1:height, x1:width]

    # 1) Generic circles.
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=max(55, round(80 * width / 1024)),
        param1=120,
        param2=35,
        minRadius=max(24, round(35 * width / 1024)),
        maxRadius=max(38, round(58 * width / 1024)),
    )

    if circles is not None:
        detected = sorted(
            np.round(circles[0]).astype(int),
            key=lambda c: c[0],
        )

        for idx, (cx, cy, radius) in enumerate(detected, start=1):
            px = x1 + int(cx)
            py = y1 + int(cy)
            cv2.circle(frame, (px, py), int(radius), (255, 255, 0), 2)
            cv2.putText(
                frame,
                f"S{idx}",
                (px - 15, py - int(radius) - 7),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 0),
                2,
            )

    # 2) Real skill templates.
    vision = VisionEngine(
        reference_size=(1020, 793),
        roi_resolver=template_roi_for,
        template_reference_size=TEMPLATE_REFERENCE_SIZE,
    )

    print("Wykryte template'y:")
    found_any = False

    runtime_plan = list(SKILL_PLAN) + list(GLOBAL_SKILL_PLAN)

    for skill_name, skill_id, target_mode, attack_type in runtime_plan:
        path = f"./bilder/{skill_name}.PNG"
        if not Path(path).exists():
            continue

        match = vision.match(
            frame,
            path,
            confidence=0.62,
            grayscale=False,
            scales=(0.92, 0.97, 1.00, 1.03, 1.08),
        )

        if match["score"] < 0.62 or not match["box"]:
            continue

        found_any = True
        x, y, w, h = match["box"]

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            f"{skill_name} {match['score']:.2f}",
            (x, max(18, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (0, 255, 0),
            1,
        )

        print(
            f"  {skill_name}/{skill_id}: "
            f"score={match['score']:.3f}, "
            f"center={match['center']}"
        )

    if not found_any:
        print("  Brak matchy >= 0.62.")

    debug = Path("./debug")
    debug.mkdir(parents=True, exist_ok=True)
    out = debug / "livearena_skill_detection.png"
    cv2.imwrite(str(out), frame)

    print("")
    print("Zapisano:", out.resolve())
    print("CYAN S1/S2/... = realne okrągłe sloty.")
    print("ZIELONE = faktycznie rozpoznane template'y.")
    print("Bot nie przypisuje już stałej pozycji do A1/A2/A3/A4.")
    print("Pasywka P nie jest elementem SKILL_PLAN i nie jest klikana.")

    try:
        os.startfile(str(out.resolve()))
    except Exception:
        pass


if __name__ == "__main__":
    main()
