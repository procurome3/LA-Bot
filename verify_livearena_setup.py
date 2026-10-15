from pathlib import Path
import importlib
import py_compile
import sys

ROOT = Path(__file__).resolve().parent

PYTHON_FILES = [
    "arenalive.py",
    "livearena_config.py",
    "livearena_vision.py",
    "livearena_runtime.py",
    "livearena_windows.py",
    "livearena_calibration.py",
    "livearena_combat.py",
    "combat_replay_test.py",
    "closeadds.py",
]

DEPENDENCIES = [
    "cv2",
    "numpy",
    "mss",
    "pyautogui",
    "keyboard",
]

CORE_TEMPLATES = [
    "arena_live_find_opponent.PNG",
    "arena_live_pick_your_champions.PNG",
    "arena_live_your_turn.PNG",
    "live_arena_ban_champions.PNG",
    "live_arena_pick_leader.PNG",
    "arena_live_confirm_pick.PNG",
    "arena_live_filter.PNG",
    "arena_live_stoneskin.PNG",
]


def main():
    ok = True

    print("=== Live Arena V10 verifier ===")
    print("Folder:", ROOT)
    print()

    for filename in PYTHON_FILES:
        path = ROOT / filename
        if not path.exists():
            print(f"[BRAK] {filename}")
            ok = False
            continue

        try:
            py_compile.compile(
                str(path),
                cfile=str(ROOT / f".__verify_{filename}.pyc"),
                doraise=True,
            )
            print(f"[OK] składnia: {filename}")
        except Exception as exc:
            print(f"[BŁĄD] składnia {filename}: {exc}")
            ok = False
        finally:
            try:
                (ROOT / f".__verify_{filename}.pyc").unlink(missing_ok=True)
            except Exception:
                pass

    print()
    for module in DEPENDENCIES:
        try:
            imported = importlib.import_module(module)
            version = getattr(imported, "__version__", "")
            suffix = f" {version}" if version else ""
            print(f"[OK] pakiet: {module}{suffix}")
        except Exception as exc:
            print(f"[BRAK] pakiet: {module} ({exc})")
            ok = False

    print()
    sys.path.insert(0, str(ROOT))
    try:
        import livearena_config as cfg
        import livearena_combat as combat

        for symbol in [
            "SKILL_PLAN",
            "GLOBAL_SKILL_PLAN",
            "ARENA_CLOSED_RECHECK_SECONDS",
            "COMBAT_SKILL_SCORE_MIN",
            "SKILL_SLOT_SCORE_MIN",
            "ALLY_ACTIVE_RING_REGIONS",
            "ALLY_DEAD_CONFIRM_FRAMES",
        ]:
            if hasattr(cfg, symbol):
                print(f"[OK] config symbol: {symbol}")
            else:
                print(f"[BRAK] config symbol: {symbol}")
                ok = False

        if hasattr(combat, "CombatEngine"):
            print("[OK] livearena_combat.CombatEngine")
        else:
            print("[BRAK] livearena_combat.CombatEngine")
            ok = False

        if hasattr(combat, "CombatAnalyzer"):
            print("[OK] livearena_combat.CombatAnalyzer")
        else:
            print("[BRAK] livearena_combat.CombatAnalyzer")
            ok = False
    except Exception as exc:
        print(f"[BŁĄD] V10 import test: {exc}")
        ok = False
    finally:
        try:
            sys.path.remove(str(ROOT))
        except ValueError:
            pass

    print()
    bilder = ROOT / "bilder"
    if not bilder.exists():
        print(
            "[INFO] folder bilder nie jest częścią paczki V10. "
            "Powinien już istnieć w Twoim raid-scripts."
        )
    else:
        for filename in CORE_TEMPLATES:
            path = bilder / filename
            if path.exists():
                print(f"[OK] bilder/{filename}")
            else:
                print(f"[BRAK] bilder/{filename}")
                ok = False

    print()
    if ok:
        print("WYNIK: OK - konfiguracja V10 jest gotowa.")
    else:
        print("WYNIK: są braki/błędy. Sprawdź wpisy oznaczone [BRAK]/[BŁĄD].")


if __name__ == "__main__":
    main()
