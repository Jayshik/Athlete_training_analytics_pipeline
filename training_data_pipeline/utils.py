from collections.abc import Iterable
from typing import Any, Callable


def nested_enumerate(
    nested_iterable: Iterable,
    start: int = 0,
    key: Callable[[Any], Any | Iterable] | None = None,
    nested_index: tuple[int, ...] = (),
):
    for i, el in enumerate(nested_iterable, start=start):
        yield (nested_index + (i,), el)
        nested_iterable = el if key is None else key(el)
        if isinstance(nested_iterable, Iterable):
            yield from nested_enumerate(
                nested_iterable, start, key, nested_index + (i,)
            )


def flatten_nested_repeatable_iterable(
    nested_repeatable_iterable: Iterable,
    nested_iterable_key: Callable[[Any], Iterable],
    repeatable_key: Callable[[Any], int],
):
    for el in nested_repeatable_iterable:
        nested_repeatable_iterable = nested_iterable_key(el)
        if isinstance(nested_repeatable_iterable, Iterable):
            for _ in range(repeatable_key(el)):
                yield from flatten_nested_repeatable_iterable(
                    nested_repeatable_iterable, nested_iterable_key, repeatable_key
                )
        else:
            yield el


def format_duration(duration):
    """
    Formats the duration into a more readable string format.

    Args:
        duration (str): Duration in "HH:MM:SS" format.

    Returns:
        str: Formatted duration.
    """
    hours, minutes, seconds = map(int, duration.split(":"))
    total_seconds = hours * 3600 + minutes * 60 + seconds

    if total_seconds < 55:
        return f'{total_seconds}"'
    if total_seconds < 3600:
        if seconds < 10:
            return f"{minutes}'"
        elif seconds > 50:
            return f"{minutes + 1}'"
        elif 20 < seconds < 30:
            return f"{minutes}'30"
        else:
            return f"{minutes}'{seconds}"
    if minutes < 5:
        return f"{hours}h"
    return f"{hours}h {minutes}m"


def time_to_seconds(time_str):
    """
    Converts time from "HH:MM:SS" format to seconds.

    Args:
        time_str (str): Time in "HH:MM:SS" format.

    Returns:
        int: Time in seconds.
    """
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s
