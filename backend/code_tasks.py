from typing import Dict, Optional, List, Tuple, Any
from pydantic import BaseModel


class CodeSubmission(BaseModel):
    """
    Data model for a single code submission coming from the frontend.
    """
    session_id: str
    exercise_id: str  # e.g. "add_two", "reverse_string", "sum_list"
    code: str
    total_time_ms: float
    first_key_delay_ms: Optional[float] = None
    client_timestamp_ms: Optional[float] = None
    code_length: Optional[int] = None
    starter_code_length: Optional[int] = None
    typing_duration_ms: Optional[float] = None


def _get_tests_for_exercise(exercise_id: str) -> Tuple[str, List[Tuple[Any, Any]]]:
    """
    Return the function name and a list of (input, expected_output) test cases
    for a given exercise_id.
    """
    if exercise_id == "add_two":
        func_name = "add_two"
        tests = [
            (3, 5),
            (-1, 1),
            (10, 12),
        ]
    elif exercise_id == "reverse_string":
        func_name = "reverse_string"
        tests = [
            ("abc", "cba"),
            ("", ""),
            ("hello", "olleh"),
        ]
    elif exercise_id == "sum_list":
        func_name = "sum_list"
        tests = [
            ([1, 2, 3], 6),
            ([], 0),
            ([5, -2, 10], 13),
        ]
    else:
        raise ValueError(f"Unknown exercise_id: {exercise_id}")

    return func_name, tests


def grade_code(submission: CodeSubmission) -> Dict[str, Optional[float]]:
    """
    Very simple, controlled grading of code for three exercises:
    - add_two(x)
    - reverse_string(s)
    - sum_list(lst)

    Executes user code in a restricted namespace and runs basic tests.
    In a production system, you would want a stronger sandbox.
    """
    code = submission.code
    exercise_id = submission.exercise_id

    try:
        func_name, tests = _get_tests_for_exercise(exercise_id)
    except ValueError as e:
        return {
            "is_correct": False,
            "tests_passed": 0,
            "tests_failed": None,
            "error": str(e),
        }

    # Restricted namespace for executing user code
    namespace: Dict[str, object] = {}

    try:
        # Execute the user code in a local namespace
        exec(code, {}, namespace)
    except Exception as e:
        return {
            "is_correct": False,
            "tests_passed": 0,
            "tests_failed": len(tests),
            "error": f"Code execution error: {e}",
        }

    if func_name not in namespace or not callable(namespace[func_name]):
        return {
            "is_correct": False,
            "tests_passed": 0,
            "tests_failed": len(tests),
            "error": f"Function {func_name} is not defined correctly.",
        }

    func = namespace[func_name]

    passed = 0
    failed = 0

    for args, expected in tests:
        try:
            if not isinstance(args, tuple):
                args_tuple = (args,)
            else:
                args_tuple = args
            result = func(*args_tuple)
            if result == expected:
                passed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    is_correct = (failed == 0)

    return {
        "is_correct": is_correct,
        "tests_passed": passed,
        "tests_failed": failed,
        "error": None,
    }
