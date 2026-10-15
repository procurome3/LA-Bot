"""Konfiguracja Live Arena bota.

Ten plik ma zawierać priorytety, progi i ROI, żeby nie trzeba było
edytować głównej logiki w arenalive.py.
"""
from pathlib import Path

# -------------------------
# Draft priorities
# -------------------------
MY_CHAMPIONS = [
    "arena_live_fabian",
    "arena_live_harima",
    "arena_live_mikage",
    "arena_live_fenax",
    "arena_live_ankora",
    "arena_live_ronda",
    "arena_live_mithrala",
    "arena_live_udk",
]

# Priorytet wyboru lidera.
# Bazowe nazwy są ważne, bo state machine zna kolejność slotów,
# więc nie musi polegać wyłącznie na osobnych PNG "arena_live_lead_*".
LEADER_PRIORITY = [
    "arena_live_fabian",
    "arena_live_ankora",
    "arena_live_harima",
    "arena_live_mikage",
]

# Zostawione dla kompatybilności z istniejącymi template'ami.
LEAD_CHAMPIONS = [
    "arena_live_lead_fabian",
    "arena_live_lead_ankora",
    "arena_live_lead_harima",
    "arena_live_lead_mikage",
]

# Sloty naszej piątki w ekranie Pick Leader (referencja 1020x793).
# Kolejność = kolejność, w której championy zostały wybrane w drafcie.
OWN_TEAM_SLOT_POINTS = [
    (98, 295),
    (190, 295),
    (282, 295),
    (145, 420),
    (238, 420),
]

BAN_CHAMPIONS = [
    "arena_live_ban_predator",
    "arena_live_ban_solonar",
]


# -------------------------
# Draft profile system V15.2
# -------------------------
# Każdy użytkownik może mieć własny JSON w ./draft_profiles bez edycji kodu.
# CLI: py arenalive.py --draft-profile nazwa
# ENV: LIVEARENA_DRAFT_PROFILE=nazwa
ACTIVE_DRAFT_PROFILE = "default"
DRAFT_PROFILES_DIR = "./draft_profiles"
DRAFT_PROFILE_ENV = "LIVEARENA_DRAFT_PROFILE"

# -------------------------
# State machine
# -------------------------
STATE_IDLE = "IDLE"
STATE_MATCHMAKING = "MATCHMAKING"
STATE_PICK = "PICK"
STATE_BAN = "BAN"
STATE_LEADER = "LEADER"
STATE_LOADING = "LOADING"
STATE_COMBAT = "COMBAT"
STATE_RESULT = "RESULT"
STATE_DONE = "DONE"

STATE_CONFIRM_FRAMES = 2
STATE_TICK_SECONDS = 0.05
DRAFT_URGENT_AFTER = 8.0
COMBAT_ACTION_BUDGET_SECONDS = 2.6

PERF_LOG_INTERVAL_SECONDS = 20.0

# -------------------------
# Live Arena availability
# -------------------------
# Jeśli po wejściu do Live Areny nie ma aktywnego Find Opponent,
# traktujemy Arenę jako zamkniętą/niedostępną i wstrzymujemy kolejne próby.
ARENA_CLOSED_RECHECK_SECONDS = 900.0
ARENA_READY_TIMEOUT_SECONDS = 4.0
MATCHMAKING_CLICK_VERIFY_SECONDS = 2.0

# -------------------------
# Combat thresholds V10
# -------------------------
COMBAT_SKILL_SCORE_MIN = 0.72
COMBAT_SKILL_SCORE_STRONG = 0.88
COMBAT_SKILL_CONFIRM_FRAMES = 2
COMBAT_ACTION_LOCK_SECONDS = 0.45
COMBAT_NO_SKILL_LOG_SECONDS = 1.0
COMBAT_NO_PROGRESS_DIAG_SECONDS = 8.0

# -------------------------
# Combat recognition V11
# -------------------------
# V11 nie przeszukuje już całego paska jednym template-matchem jako
# podstawowej metody. Najpierw wykrywa fizyczne okrągłe przyciski,
# normalizuje ich obrazy, a potem klasyfikuje je względem PNG z bilder.
SKILL_SLOT_SCORE_MIN = 0.46
SKILL_SLOT_SCORE_STRONG = 0.62
SKILL_FAMILY_BIND_SCORE = 0.50
SKILL_FAMILY_MEMORY_MIN = 0.40

# -------------------------
# Scalable roster identity V15
# -------------------------
# The combat database can be large, but only the actually drafted team should
# receive expensive A1 verification.  If draft hints are unavailable, a cheap
# low-resolution prefilter bounds the number of exact A1 matches.
COMBAT_A1_EXACT_SCAN_LIMIT = 8
COMBAT_A1_PREFILTER_TOP_K = 5
COMBAT_A1_PREFILTER_MAX_EXACT = 8
COMBAT_A1_PREFILTER_DOWNSCALE = 0.33
COMBAT_A1_PREFILTER_RESCUE_SCORE = 0.78
COMBAT_A1_PREFILTER_RESCUE_MARGIN = 0.16

# Jeśli przez ten czas mamy pewne Your Turn / zielony ring, ale żaden
# template nie przejdzie progu, klikamy LEWY pierwszy aktywny skill.
# Dla obecnej puli championów jest to A1 wymagające celu.
SKILL_SAFE_A1_FALLBACK_SECONDS = 0.75

# Wykrywanie zielonego ringu aktywnego ally.
ACTIVE_RING_GREEN_RATIO_MIN = 0.0030
ACTIVE_RING_DOMINANCE = 1.80

# Jawna kolejność skilli. Kolejność listy SKILL_PLAN nie jest już
# bezpośrednio używana jako kolejność decyzji.
SKILL_PRIORITY_BY_FAMILY = {
    # Existing roster — behavior preserved.
    "fabian": ["A3", "A2", "A1"],
    "mikage": ["A3", "A2", "A1"],
    "mithrala": ["A3", "A2", "A1"],
    "ankora": ["A3", "A2", "A1"],
    "udk": ["A3", "A2", "A1"],
    "ronda": ["A2", "A3", "A1"],
    "harima": ["A2", "A3", "A1"],
    "fenax": ["A1"],

    # User-defined new roster.
    "predator": ["A2", "A3", "A1"],
    "mavara": ["A3", "A2", "A1"],
    "maria": ["A3", "A2", "A1"],
    "pelops": ["A3", "A2", "A1"],
    "galathir_f1": ["A3", "A2", "A1"],
    "galathir_f2": ["A3", "A2", "A1"],
    "theodosia_f1": ["A2", "A3", "A1"],
    "theodosia_f2": ["A2", "A3", "A1"],
    "komidus_f1": ["A4", "A1"],
    "komidus_f2": ["A3", "A2", "A1"],
    "arbiter": ["A3", "A4", "A2", "A1"],
    "vestele": ["A3", "A2", "A1"],
    "tekteon": ["A3", "A2", "A1"],
    "siphi": ["A3", "A2", "A1"],
    "krixia_f1": ["A3", "A4", "A1"],
    "krixia_f2": ["A3", "A2", "A4", "A1"],
    "harvest_jack": ["A2", "A3", "A1"],
    "joan_f1": ["A3", "A2", "A1"],
    "joan_f2": ["A3", "A2", "A1"],
    "yumeko": ["A3", "A1"],
    "cruetraxa": ["A2", "A1"],
    "gliseah": ["A3", "A2", "A1"],
    "nekhret": ["A2", "A3", "A1"],
    "embrys_f1": ["A4", "A1"],
    "embrys_f2": ["A2", "A3", "A1"],
    "marius": ["A3", "A2", "A1"],
}

# Conditions are evaluated only for the currently recognised champion/skill.
# "unknown" perception never silently falls through to a lower priority skill.
SKILL_RULES_BY_FAMILY = {
    "fabian": {
        "A3": {"opening_skip_if_enemy_any": ("gliseah",)},
    },
    "maria": {
        "A3": {"self_buff_count_in": (3, 6, 9)},
        "A2": {"requires_extra_turn": True},
    },
    "theodosia_f1": {"A3": {"requires_dead_ally": True}},
    "theodosia_f2": {"A3": {"requires_dead_ally": True}},
    "arbiter": {"A4": {"requires_dead_ally": True}},
    "siphi": {"A3": {"requires_dead_ally": True}},
    "joan_f1": {"A3": {"requires_dead_ally": True}},
}

# Target policy is applied after the global safety filter
# (Block Damage / Unkillable / Counterattack) and before final HP/slot fallback.
TARGET_POLICY_BY_FAMILY_SKILL = {
    ("fabian", "A2"): {
        "avoid_effects": ("stoneskin", "total_guard", "block_debuffs"),
        "strict_avoid": True,
    },
    ("vestele", "A2"): {
        "avoid_effects": ("unkillable", "total_guard"),
        "strict_avoid": True,
        "unknown_is_unsafe_effects": ("unkillable",),
    },
    ("maria", "A1"): {
        "prefer_effects": ("total_guard",),
    },
    ("yumeko", "A1"): {
        "prefer_effects": ("total_guard",),
    },
    ("harvest_jack", "A1"): {
        "buff_count": "max",
    },
    ("cruetraxa", "A2"): {
        "buff_count": "min",
        "avoid_effects": ("unkillable",),
    },
    ("cruetraxa", "A1"): {
        "buff_count": "min",
        "avoid_effects": ("unkillable",),
    },
}

# Local status templates used by skill-specific target rules.
SPECIAL_TARGET_EFFECT_TEMPLATES = {
    "block_debuffs": "./bilder/block_debuffs.png",
    "total_guard": "./bilder/total_guard.png",
    "mercurial": "./bilder/total_guard.png",
}
SPECIAL_TARGET_EFFECT_SCORE_MIN = 0.78
SPECIAL_TARGET_EFFECT_SCALES = (0.80, 0.90, 1.00, 1.10, 1.20)

# Transform A4 jest globalny i wpada przed A1, ale po wyższych
# aktywnych skillach A2/A3 zgodnie z priorytetem championa.
GLOBAL_A4_BEFORE_A1 = True

# Cooldown / disabled skill: porównujemy jasność i nasycenie realnej ikony
# do aktywnego PNG z bilder. Chroni to przed wyborem skilla na cooldownie.
SKILL_AVAILABLE_VALUE_RATIO_MIN = 0.62
SKILL_AVAILABLE_SAT_RATIO_MIN = 0.50

# Single-target: po wybraniu skilla daj RAID chwilę na wejście w target mode.
TARGETING_DELAY_MIN = 0.14
TARGETING_DELAY_MAX = 0.22
TARGET_RETRY_DELAY = 0.14

# New decision runtime tuning
# These values are intentionally conservative: the engine waits a short time,
# then re-evaluates with a controlled fallback instead of waiting forever.
DECISION_UNKNOWN_TIMEOUT = 1.0
DECISION_ALLOW_FALLBACK = True
TARGET_CONFIRM_RETRY_COUNT = 3
TARGET_CONFIRM_WAIT_SECONDS = 0.12
REVIVE_CONFIRM_FRAMES = 4

# Leader selection verify V11.3.
LEADER_SELECTED_BORDER_RATIO_MIN = 0.12
LEADER_SELECTED_BORDER_MARGIN = 0.05
LEADER_TEMPLATE_CONFIDENCE = 0.70

# Combat turn gate.
# Ring służy wyłącznie do identyfikacji aktywnego ally.
# Nie jest już dowodem własnej tury.
COMBAT_REQUIRE_YOUR_TURN = True

# V11.4: główne źródło informacji o turze w walce.
COMBAT_PLAYER_PORTRAIT_REGION = (280, 0, 390, 105)
COMBAT_OPPONENT_PORTRAIT_REGION = (635, 0, 755, 105)
COMBAT_PORTRAIT_GREEN_RATIO_MIN = 0.025
COMBAT_PORTRAIT_GREEN_DOMINANCE = 2.0
BATTLE_READY_CONFIRM_FRAMES = 2

ALLY_ACTIVE_RING_REGIONS = {
    1: (50, 420, 225, 650),
    2: (215, 445, 405, 700),
    3: (450, 470, 680, 765),
    4: (715, 445, 925, 710),
}

ENEMY_HP_ALIVE_THRESHOLD = 0.010

# Revive jest celowo konserwatywny: slot musi najpierw zostać
# potwierdzony jako żywy, a dopiero potem zniknięcie HP może oznaczać śmierć.
ALLY_HP_ALIVE_THRESHOLD = 0.008
ALLY_HP_DEAD_THRESHOLD = 0.002
ALLY_ALIVE_CONFIRM_FRAMES = 3
ALLY_DEAD_CONFIRM_FRAMES = 4

# -------------------------
# Combat skill plan
# -------------------------
# tuple: template, skill_id, target_mode, attack_type
#
# skill_id ("A1", "A2", "A3", "A4"... ) jest nazwą logiczną.
# Bot klika środek faktycznie znalezionego template'u skilla.
#
# attack_type:
#   single    -> affinity-aware
#   targeted  -> wymaga celu, affinity bez znaczenia
#   aoe       -> bez pojedynczego target click
#   self        -> support/buff; engine potwierdza na aktywnym modelu, gdy UI tego wymaga
#   ally_dead   -> po skillu wybiera martwego sojusznika
#   ally_living -> po skillu wybiera żywego sojusznika (np. lowest HP)
#   transform   -> A4 mitycznych; A4 -> klik aktywnego modelu championa

GLOBAL_SKILL_PLAN = [
    ("skill_mythical_transform_a4", "A4", "normal", "transform"),
]

SKILL_PLAN = [
    ("skill_fabian_a3", "A3", "normal", "aoe"),
    ("skill_fabian_a2", "A2", "normal", "single"),
    ("skill_fabian_a1", "A1", "normal", "single"),
    ("skill_mikage_a3", "A3", "normal", "single"),
    ("skill_mikage_a2", "A2", "normal", "aoe"),
    ("skill_mikage_a1", "A1", "normal", "single"),
    ("skill_mithrala_a3", "A3", "normal", "self"),
    ("skill_mithrala_a2", "A2", "normal", "aoe"),
    ("skill_mithrala_a1", "A1", "normal", "targeted"),
    ("skill_ankora_a3", "A3", "dead_ally", "ally_dead"),
    ("skill_ankora_a2", "A2", "normal", "self"),
    ("skill_ankora_a1", "A1", "normal", "single"),
    ("skill_udk_a3", "A3", "normal", "self"),
    ("skill_udk_a2", "A2", "normal", "aoe"),
    ("skill_udk_a1", "A1", "normal", "single"),
    ("skill_ronda_a2", "A2", "normal", "single"),
    ("skill_ronda_a3", "A3", "normal", "aoe"),
    ("skill_ronda_a1", "A1", "normal", "single"),
    ("skill_harima_a2", "A2", "lowest_hp", "single"),
    ("skill_harima_a3", "A3", "normal", "aoe"),
    ("skill_harima_a1", "A1", "normal", "single"),
    ("skill_fenax_a1", "A1", "normal", "single"),
]

# Vision ROIs
REFERENCE_SIZE = (1020, 793)
TEMPLATE_REFERENCE_SIZE = (1024, 769)

ROI_TOP_CENTER = (330, 20, 700, 145)
ROI_PHASE_CENTER = (360, 170, 670, 480)
ROI_FILTER_LEFT = (0, 520, 130, 793)
ROI_CONFIRM = (735, 600, 1020, 793)
ROI_ENEMY_TEAM = (610, 150, 1020, 570)
ROI_OWN_TEAM = (0, 150, 430, 570)
ROI_CHAMPION_ROSTER = (65, 555, 790, 793)
ROI_SKILL_BAR = (390, 590, 1020, 793)
ALLY_SLOT_POINTS = {
    1: (145, 455),
    2: (300, 505),
    3: (560, 535),
    4: (815, 505),
}
ALLY_HP_REGIONS = {
    1: (92, 338, 185, 390),
    2: (250, 375, 345, 430),
    3: (510, 415, 610, 465),
    4: (765, 390, 865, 445),
}

ROI_CENTER_STATUS = (250, 250, 800, 650)
ROI_RESULT_BOTTOM = (250, 420, 800, 793)
ROI_REFILL_MODAL = (220, 150, 820, 690)
ROI_REFILL_CONFIRM = (300, 370, 800, 720)
ROI_FIND_OPPONENT = (300, 480, 1020, 793)


def template_roi_for(template_path):
    """Zwraca ROI dla template'u albo None, jeśli lepiej użyć całej klatki."""
    name = Path(template_path).name.lower()

    if name == "arena_live_your_turn.png":
        return ROI_TOP_CENTER

    if name in {
        "arena_live_pick_your_champions.png",
        "live_arena_ban_champions.png",
        "live_arena_pick_leader.png",
    }:
        return ROI_PHASE_CENTER

    if name == "arena_live_filter.png":
        return ROI_FILTER_LEFT

    if name == "arena_live_confirm_pick.png":
        return ROI_CONFIRM

    if name.startswith("arena_live_ban_"):
        return ROI_ENEMY_TEAM

    if name.startswith("arena_live_enemy_"):
        return ROI_ENEMY_TEAM

    if name.startswith("arena_live_lead_"):
        return ROI_OWN_TEAM

    if name.startswith("skill_"):
        return ROI_SKILL_BAR

    if name in {
        "arena_live_opponent_left.png",
        "arena_live_cant_find_opponent.png",
    }:
        return ROI_CENTER_STATUS

    if name == "arena_live_return.png":
        return ROI_RESULT_BOTTOM

    if name == "live_arena_refyll_modal.png":
        return ROI_REFILL_MODAL

    if name == "arena_live_find_opponent.png":
        return ROI_FIND_OPPONENT

    if name in {
        "arena_live_confirm_refyll.png",
        "arena_live_10gem_refyll.png",
    }:
        return ROI_REFILL_CONFIRM

    champion_names = {f"{x.lower()}.png" for x in MY_CHAMPIONS}
    if name in champion_names:
        return ROI_CHAMPION_ROSTER

    return None
