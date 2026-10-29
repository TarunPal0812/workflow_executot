import time
from typing import Any, Optional


def run_step(step: dict[str, Any], value: str) -> str:
    kind = step.get("type")

    if kind == "text_transform":
        op = step.get("operation")
        if not op:
            raise ValueError("Text transformation step is missing 'operation'")

        if op in ("uppercase", "upppercase"):
            return value.upper()
        if op == "lowercase":
            return value.lower()
        if op in ("trim", "strip"):
            return value.strip()
        if op == "reverse":
            return value[::-1]
        if op == "capitalize":
            return value.capitalize()
        if op == "title":
            return value.title()
        if op == "length":
            return str(len(value))
        if op == "replace":
            find_str = step.get("value") or ""
            replace_str = step.get("replace_with") or ""
            return value.replace(find_str, replace_str)

        raise ValueError(f"Unknown text transformation operation: '{op}'")

    if kind in ("arithmetic", "arithmatic"):
        try:
            x = float(value)
        except ValueError:
            raise ValueError(
                f"Input '{value}' is not a valid number for arithmetic step"
            )

        if "operand" not in step or step.get("operand") is None:
            raise ValueError("Arithmetic step requires numeric 'operand'")

        try:
            y = float(step["operand"])
        except ValueError:
            raise ValueError(
                f"Invalid operand '{step.get('operand')}'; must be numeric"
            )

        op = step.get("operation") or step.get("operations")
        if not op:
            raise ValueError("Arithmetic step is missing 'operation'")

        if op in ("add", "+"):
            result = x + y
        elif op in ("subtract", "-"):
            result = x - y
        elif op in ("multiply", "*"):
            result = x * y
        elif op in ("division", "divide", "/"):
            if y == 0:
                raise ZeroDivisionError("Cannot divide by 0")
            result = x / y
        elif op in ("power", "**"):
            result = x**y
        elif op in ("modulo", "%"):
            if y == 0:
                raise ZeroDivisionError("Cannot modulo by 0")
            result = x % y
        else:
            raise ValueError(f"Unknown arithmetic operation: '{op}'")

        if result.is_integer():
            return str(int(result))
        return f"{result:.6f}".rstrip("0").rstrip(".")

    raise ValueError(f"Unknown step type: '{kind}'")


def execute_workflow(
    steps: list[dict[str, Any]],
    initial_input: str,
    start: int = 0,
    previous_results: Optional[list[dict[str, Any]]] = None,
) -> tuple[str, Optional[str], Optional[str], list[dict[str, Any]]]:
    if not steps:
        return "completed", initial_input, None, []

    results: list[dict[str, Any]] = list(previous_results or [])[:start]

    if start > 0 and results:
        current_value = str(results[start - 1].get("output", initial_input))
    else:
        current_value = initial_input
        start = 0

    for i in range(start, len(steps)):
        step = steps[i]
        step_type = step.get("type", "unknown")
        step_op = step.get("operation") or step.get("operations")
        start_time = time.perf_counter()

        try:
            output_val = run_step(step, current_value)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            results.append(
                {
                    "index": i,
                    "type": step_type,
                    "operation": step_op,
                    "input": current_value,
                    "output": output_val,
                    "status": "success",
                    "error": None,
                    "duration_ms": duration_ms,
                }
            )
            current_value = output_val

        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            error_msg = str(e)
            results.append(
                {
                    "index": i,
                    "type": step_type,
                    "operation": step_op,
                    "input": current_value,
                    "output": None,
                    "status": "failed",
                    "error": error_msg,
                    "duration_ms": duration_ms,
                }
            )
            return (
                "failed",
                None,
                f"Step {i + 1} ({step_type}) failed: {error_msg}",
                results,
            )

    return "completed", current_value, None, results
