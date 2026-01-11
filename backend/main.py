from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from statistics import mean, pstdev
from math import isnan

from data_store import save_event, get_events_by_session
from code_tasks import CodeSubmission, grade_code

app = FastAPI()

# Allow frontend (Vite/React) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SegmentEvent(BaseModel):
    """
    Data model for reading task events.
    """
    session_id: str
    segment_id: int
    text_length: int
    reading_time_ms: float
    client_timestamp_ms: Optional[float] = None


class ReactionEvent(BaseModel):
    """
    Data model for reaction-time task events.
    """
    session_id: str
    question_index: int
    reaction_time_ms: float
    is_correct: bool
    client_timestamp_ms: Optional[float] = None
    chosen_option_index: Optional[int] = None


def compute_basic_stats(values: List[float]) -> Dict[str, Optional[float]]:
    """
    Compute basic statistics (mean, std, min, max) for a list of numeric values.
    Returns None for all fields if the list is empty.
    """
    if not values:
        return {
            "count": 0,
            "avg_ms": None,
            "std_ms": None,
            "min_ms": None,
            "max_ms": None,
        }

    if len(values) > 1:
        std_value = pstdev(values)
    else:
        std_value = 0.0

    return {
        "count": len(values),
        "avg_ms": mean(values),
        "std_ms": std_value,
        "min_ms": min(values),
        "max_ms": max(values),
    }


@app.get("/health")
def health_check():
    """
    Simple health check to verify that backend is running.
    """
    return {"status": "ok"}


@app.post("/segment")
def receive_segment(event: SegmentEvent):
    """
    Receive a reading segment event from frontend.
    Save event to data.json via data_store.
    """
    save_event(event.dict())
    return {"status": "saved"}


@app.post("/reaction")
def receive_reaction(event: ReactionEvent):
    """
    Receive a reaction-time event from frontend.
    Save event to data.json via data_store.
    """
    save_event(event.dict())
    return {"status": "saved"}


@app.post("/code")
def receive_code(submission: CodeSubmission):
    """
    Receive a code submission event, grade it using code_tasks.grade_code,
    and save the full event (including grading result) into data.json.
    """
    grading = grade_code(submission)
    event_dict = submission.dict()
    event_dict.update(
        {
            "type": "code",
            "is_correct": grading.get("is_correct"),
            "tests_passed": grading.get("tests_passed"),
            "tests_failed": grading.get("tests_failed"),
            "grading_error": grading.get("error"),
        }
    )
    save_event(event_dict)
    return {
        "status": "saved",
        "is_correct": grading.get("is_correct"),
        "tests_passed": grading.get("tests_passed"),
        "tests_failed": grading.get("tests_failed"),
        "error": grading.get("error"),
    }

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a numeric value into [min_val, max_val].
    """
    return max(min_val, min(max_val, value))


def normalize_inverse(value: Optional[float], good_low: float, bad_high: float) -> float:
    """
    Normalize a value where smaller is better into [0,1].
    good_low  -> 1.0
    bad_high  -> 0.0
    Values outside the range are clamped.
    If value is None, return 0.5 (neutral).
    """
    if value is None or isnan(value):
        return 0.5
    if value <= good_low:
        return 1.0
    if value >= bad_high:
        return 0.0
    # Linear interpolation between good_low and bad_high
    return 1.0 - (value - good_low) / (bad_high - good_low)


def normalize_direct(value: Optional[float], bad_low: float, good_high: float) -> float:
    """
    Normalize a value where larger is better into [0,1].
    bad_low   -> 0.0
    good_high -> 1.0
    Values outside the range are clamped.
    If value is None, return 0.5 (neutral).
    """
    if value is None or isnan(value):
        return 0.5
    if value <= bad_low:
        return 0.0
    if value >= good_high:
        return 1.0
    return (value - bad_low) / (good_high - bad_low)


def safe_cv(avg: Optional[float], std: Optional[float]) -> Optional[float]:
    """
    Compute coefficient of variation (std / mean) safely.
    If avg is None or non-positive, return None.
    """
    if avg is None or std is None or avg <= 0:
        return None
    return std / avg

def compute_concentration_profile(
    reading_stats: Dict[str, Optional[float]],
    reaction_stats: Dict[str, Optional[float]],
    reaction_events: List[Dict],
    code_summary: Dict[str, Optional[float]],
    code_events: List[Dict],
) -> Dict:
    """
    Compute a concentration profile (overall score + per-component scores)
    based on stability and consistency across tasks.
    All scores are normalized into [0,100].
    """

    # ----- Reading component -----
    reading_cv = safe_cv(reading_stats.get("avg_ms"), reading_stats.get("std_ms"))
    # Assume CV in [0.1, 0.7] where <=0.1 is very stable, >=0.7 is quite unstable
    reading_stability = normalize_inverse(reading_cv, good_low=0.1, bad_high=0.7)
    reading_score = reading_stability * 100.0

    # ----- Reaction component -----
    reaction_cv = safe_cv(reaction_stats.get("avg_ms"), reaction_stats.get("std_ms"))
    reaction_stability = normalize_inverse(reaction_cv, good_low=0.15, bad_high=0.8)

    # Reaction accuracy from stats (we compute it later in get_summary, but can recompute here)
    if reaction_events:
        correct_count = sum(1 for e in reaction_events if e.get("is_correct") is True)
        reaction_accuracy = correct_count / len(reaction_events)
    else:
        reaction_accuracy = None

    # Assume accuracy below 0.5 is poor, above 0.9 is excellent
    accuracy_component = normalize_direct(reaction_accuracy, bad_low=0.5, good_high=0.9)

    # Trend over time: compare first half vs second half reaction times
    # to capture drift / fatigue
    trend_component: float
    if len(reaction_events) >= 4:
        # Sort by question index to preserve order
        sorted_reactions = sorted(
            reaction_events, key=lambda e: e.get("question_index", 0)
        )
        times = [
            e["reaction_time_ms"]
            for e in sorted_reactions
            if "reaction_time_ms" in e
        ]
        if len(times) >= 4:
            mid = len(times) // 2
            first_half = times[:mid]
            second_half = times[mid:]
            if first_half and second_half and mean(first_half) > 0:
                ratio = mean(second_half) / mean(first_half)
                drift = abs(ratio - 1.0)  # 0 means perfectly stable
                # Assume drift <= 0.1 is great, >= 0.6 is poor
                trend_component = normalize_inverse(drift, good_low=0.1, bad_high=0.6)
            else:
                trend_component = 0.5
        else:
            trend_component = 0.5
    else:
        trend_component = 0.5

    # Combine reaction components (stability, accuracy, trend) equally
    reaction_combined = (reaction_stability + accuracy_component + trend_component) / 3.0
    reaction_score = reaction_combined * 100.0

    # ----- Code component -----
    # Use summary values where available
    success_rate = code_summary.get("success_rate")
    # Assume success below 0.3 is poor, above 0.9 is very good
    success_component = normalize_direct(success_rate, bad_low=0.3, good_high=0.9)

    avg_typing_rate = code_summary.get("avg_typing_rate_chars_per_sec")
    # Assume typing rate in [2, 12] chars/s as a rough reasonable band
    typing_component = normalize_direct(avg_typing_rate, bad_low=2.0, good_high=12.0)

    # Initiation stability: std of first_key_delay across code events
    delays = [
        e["first_key_delay_ms"]
        for e in code_events
        if e.get("first_key_delay_ms") is not None
    ]
    if len(delays) > 1:
        delay_std = pstdev(delays)
        # Assume std <= 1500 ms is stable, >= 6000 ms is very unstable
        initiation_stability = normalize_inverse(delay_std, good_low=1500.0, bad_high=6000.0)
    else:
        initiation_stability = 0.5

    code_combined = (success_component + typing_component + initiation_stability) / 3.0
    code_score = code_combined * 100.0

    # ----- Overall score (weighted combination) -----
    # Reading: 30%, Reaction: 40%, Code: 30%
    overall_score = (
        0.3 * reading_score + 0.4 * reaction_score + 0.3 * code_score
    )

    # ----- Textual comment -----
    # Simple heuristic to give a short interpretation
    if overall_score >= 80:
        overall_comment = "Your overall concentration score is high. Performance is generally stable across tasks."
    elif overall_score >= 60:
        overall_comment = "Your overall concentration score is moderate. There are some signs of variability that may reflect attention fluctuations."
    else:
        overall_comment = "Your overall concentration score is relatively low. There is noticeable variability in performance that may reflect difficulty maintaining stable attention."

    details: List[str] = []

    # Compare components to highlight weaker/stronger areas
    # Use a simple delta threshold
    if reading_score + 10 < reaction_score and reading_score + 10 < code_score:
        details.append("Reading times are less stable compared to reaction and code tasks.")
    if reaction_score + 10 < reading_score and reaction_score + 10 < code_score:
        details.append("Reaction times show lower stability or accuracy compared to other tasks.")
    if code_score + 10 < reading_score and code_score + 10 < reaction_score:
        details.append("Code-writing behavior (initiation or typing) appears less consistent than other tasks.")

    if not details:
        details.append("No single task stands out as significantly weaker; performance is fairly balanced across tasks.")

    comment = overall_comment + " " + " ".join(details)

    return {
        "overall_score": overall_score,
        "reading_score": reading_score,
        "reaction_score": reaction_score,
        "code_score": code_score,
        "components": {
            "reading_stability_cv": reading_cv,
            "reaction_cv": reaction_cv,
            "reaction_accuracy": reaction_accuracy,
            "reaction_trend_component": trend_component,
            "code_success_rate": success_rate,
            "code_avg_typing_rate_chars_per_sec": avg_typing_rate,
        },
        "comment": comment,
    }


@app.get("/summary/{session_id}")
def get_summary(session_id: str):
    """
    Compute summary statistics for a given session_id.
    Returns separate summaries for:
    - reading segments
    - reaction events
    - code submissions
    """
    events = get_events_by_session(session_id)

    if not events:
        raise HTTPException(status_code=404, detail="No events for this session_id")

    # Separate reading, reaction, and code events
    reading_events = [e for e in events if "segment_id" in e]
    reaction_events = [e for e in events if "question_index" in e]
    code_events = [e for e in events if "exercise_id" in e]

    # ----- Reading stats -----
    reading_times = [e["reading_time_ms"] for e in reading_events]
    reading_stats = compute_basic_stats(reading_times)

    # ----- Reaction stats -----
    reaction_times = [
        e["reaction_time_ms"]
        for e in reaction_events
        if "reaction_time_ms" in e
    ]
    reaction_stats = compute_basic_stats(reaction_times)

    if reaction_events:
        correct_count = sum(1 for e in reaction_events if e.get("is_correct") is True)
        reaction_accuracy: Optional[float] = correct_count / len(reaction_events)
    else:
        reaction_accuracy = None

        # ----- Code stats -----
    if code_events:
        total_times = [
            e["total_time_ms"]
            for e in code_events
            if "total_time_ms" in e
        ]
        first_key_delays = [
            e["first_key_delay_ms"]
            for e in code_events
            if e.get("first_key_delay_ms") is not None
        ]

        total_time_stats = compute_basic_stats(total_times)
        if first_key_delays:
            first_key_stats = compute_basic_stats(first_key_delays)
        else:
            first_key_stats = {
                "count": 0,
                "avg_ms": None,
                "std_ms": None,
                "min_ms": None,
                "max_ms": None,
            }

        # Compute typing rates (characters per second)
        typing_rates: List[float] = []
        for e in code_events:
            td = e.get("typing_duration_ms")
            code_len = e.get("code_length")
            starter_len = e.get("starter_code_length")
            if (
                td is not None
                and td > 0
                and code_len is not None
                and starter_len is not None
            ):
                delta_chars = code_len - starter_len
                if delta_chars > 0:
                    rate = delta_chars / (td / 1000.0)  # chars per second
                    typing_rates.append(rate)

        if typing_rates:
            typing_rate_stats = compute_basic_stats(typing_rates)
        else:
            typing_rate_stats = {
                "count": 0,
                "avg_ms": None,
                "std_ms": None,
                "min_ms": None,
                "max_ms": None,
            }

        correct_code_count = sum(
            1 for e in code_events if e.get("is_correct") is True
        )
        code_success_rate: Optional[float] = (
            correct_code_count / len(code_events) if code_events else None
        )

        # Per-exercise breakdown
        per_exercise: Dict[str, Dict[str, Optional[float]]] = {}
        by_ex: Dict[str, List[Dict]] = {}
        for e in code_events:
            ex_id = e.get("exercise_id", "unknown")
            by_ex.setdefault(ex_id, []).append(e)

        for ex_id, ex_events in by_ex.items():
            ex_total_times = [
                ev["total_time_ms"] for ev in ex_events if "total_time_ms" in ev
            ]
            ex_first_key_delays = [
                ev["first_key_delay_ms"]
                for ev in ex_events
                if ev.get("first_key_delay_ms") is not None
            ]
            ex_time_stats = compute_basic_stats(ex_total_times)
            if ex_first_key_delays:
                ex_first_key_stats = compute_basic_stats(ex_first_key_delays)
            else:
                ex_first_key_stats = {
                    "count": 0,
                    "avg_ms": None,
                    "std_ms": None,
                    "min_ms": None,
                    "max_ms": None,
                }

            # Per-exercise typing rates
            ex_typing_rates: List[float] = []
            for ev in ex_events:
                td = ev.get("typing_duration_ms")
                code_len = ev.get("code_length")
                starter_len = ev.get("starter_code_length")
                if (
                    td is not None
                    and td > 0
                    and code_len is not None
                    and starter_len is not None
                ):
                    delta_chars = code_len - starter_len
                    if delta_chars > 0:
                        rate = delta_chars / (td / 1000.0)
                        ex_typing_rates.append(rate)

            if ex_typing_rates:
                ex_typing_stats = compute_basic_stats(ex_typing_rates)
                ex_avg_typing_rate = ex_typing_stats["avg_ms"]
            else:
                ex_avg_typing_rate = None

            ex_correct = sum(
                1 for ev in ex_events if ev.get("is_correct") is True
            )
            ex_success_rate = ex_correct / len(ex_events) if ex_events else None

            per_exercise[ex_id] = {
                "count_submissions": len(ex_events),
                "success_rate": ex_success_rate,
                "avg_total_time_ms": ex_time_stats["avg_ms"],
                "avg_first_key_delay_ms": ex_first_key_stats["avg_ms"],
                "avg_typing_rate_chars_per_sec": ex_avg_typing_rate,
            }

        code_summary = {
            "count_submissions": len(code_events),
            "success_rate": code_success_rate,
            "avg_total_time_ms": total_time_stats["avg_ms"],
            "std_total_time_ms": total_time_stats["std_ms"],
            "avg_first_key_delay_ms": first_key_stats["avg_ms"],
            "avg_typing_rate_chars_per_sec": typing_rate_stats["avg_ms"],
            "per_exercise": per_exercise,
        }
    else:
        code_summary = {
            "count_submissions": 0,
            "success_rate": None,
            "avg_total_time_ms": None,
            "std_total_time_ms": None,
            "avg_first_key_delay_ms": None,
            "per_exercise": {},
        }

    # Build concentration profile based on the aggregated stats and raw events
    concentration_profile = compute_concentration_profile(
        reading_stats=reading_stats,
        reaction_stats=reaction_stats,
        reaction_events=reaction_events,
        code_summary=code_summary,
        code_events=code_events,
    )

    summary = {
        "session_id": session_id,
        "reading": {
            "count_segments": reading_stats["count"],
            "avg_reading_time_ms": reading_stats["avg_ms"],
            "std_reading_time_ms": reading_stats["std_ms"],
            "min_reading_time_ms": reading_stats["min_ms"],
            "max_reading_time_ms": reading_stats["max_ms"],
        },
        "reaction": {
            "count_questions": reaction_stats["count"],
            "avg_reaction_time_ms": reaction_stats["avg_ms"],
            "std_reaction_time_ms": reaction_stats["std_ms"],
            "min_reaction_time_ms": reaction_stats["min_ms"],
            "max_reaction_time_ms": reaction_stats["max_ms"],
            "accuracy": reaction_accuracy,
        },
        "code": code_summary,
        "concentration": concentration_profile,
    }

    return summary
