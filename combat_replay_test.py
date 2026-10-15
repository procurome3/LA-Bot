"""Offline Combat Replay Test V11.

NICZEGO NIE KLIKA.

Przykłady:
  py combat_replay_test.py debug
  py combat_replay_test.py screenshot.png
  py combat_replay_test.py film.mp4 --crop 697,31,1024,769 --every 15

V11 pokazuje dodatkowo:
- active ally slot z zielonego ringu,
- slot -> family memory,
- fizyczne kółka skillów,
- slot-first normalized similarity,
- decyzję / target / Stone Skin / affinity.
"""

from pathlib import Path
import argparse
import json

import cv2

from livearena_config import (
    REFERENCE_SIZE,
    TEMPLATE_REFERENCE_SIZE,
    template_roi_for,
)
from livearena_vision import VisionEngine
from livearena_combat import CombatAnalyzer


def summarize(decision, analyzer):
    skill = decision.get("skill")
    scan = decision.get("skill_scan") or {}

    result = {
        "active_slot": decision.get("active_slot"),
        "ring_ratios": {
            str(k): round(v, 5)
            for k, v in (decision.get("ring_ratios") or {}).items()
        },
        "family": decision.get("selected_family"),
        "family_confidence": round(
            float(decision.get("family_confidence") or 0.0),
            3,
        ),
        "recognition_mode": scan.get("recognition_mode"),
        "circles": len(scan.get("physical_slots") or []),
        "memory": decision.get("slot_family_memory"),
        "top_skills": analyzer.top_skill_scores(decision, 10),
        "target": decision.get("target_slot"),
        "reason": decision.get("reason"),
    }

    if skill:
        result["skill"] = {
            "name": skill["skill_name"],
            "id": skill["skill_id"],
            "type": skill["attack_type"],
            "score": round(float(skill["score"]), 3),
            "center": skill.get("center"),
            "fallback": bool(skill.get("fallback", False)),
        }
    else:
        result["skill"] = None

    return result


parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("--every", type=int, default=15)
parser.add_argument(
    "--crop",
    help="x,y,w,h gdy plik zawiera cały pulpit",
)
parser.add_argument(
    "--allow-fallback",
    action="store_true",
    help="Pokaż również decyzję z bezpiecznym lewym A1 fallback.",
)
args = parser.parse_args()

crop = None
if args.crop:
    crop = tuple(int(v) for v in args.crop.split(","))
    if len(crop) != 4:
        raise SystemExit("--crop musi mieć x,y,w,h")

vision = VisionEngine(
    reference_size=REFERENCE_SIZE,
    roi_resolver=template_roi_for,
    template_reference_size=TEMPLATE_REFERENCE_SIZE,
)
analyzer = CombatAnalyzer(vision)

ally_tracker = {}
slot_family_memory = {}


def analyze_frame(frame, label):
    if crop:
        x, y, w, h = crop
        frame = frame[y:y+h, x:x+w]

    h, w = frame.shape[:2]
    rect = (0, 0, w, h)

    decision = analyzer.choose_decision(
        frame,
        rect,
        ally_tracker,
        slot_family_memory,
        allow_a1_fallback=args.allow_fallback,
    )

    print(f"\n[{label}]")
    print(
        json.dumps(
            summarize(decision, analyzer),
            indent=2,
            ensure_ascii=False,
        )
    )


source = Path(args.source)

if source.is_dir():
    paths = sorted(
        list(source.glob("*.png"))
        + list(source.glob("*.jpg"))
        + list(source.glob("*.jpeg"))
    )
    for path in paths:
        frame = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if frame is not None:
            analyze_frame(frame, path.name)
    raise SystemExit(0)

if source.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
    frame = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if frame is None:
        raise SystemExit(f"Nie udało się odczytać {source}")
    analyze_frame(frame, source.name)
    raise SystemExit(0)

capture = cv2.VideoCapture(str(source))
if not capture.isOpened():
    raise SystemExit(f"Nie udało się otworzyć {source}")

index = 0
while True:
    ok, frame = capture.read()
    if not ok:
        break

    if index % max(1, args.every) == 0:
        analyze_frame(frame, f"frame {index}")

    index += 1

capture.release()
