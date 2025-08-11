import copy
import datetime
from collections import defaultdict

from graig_nlp.summary_generation.intervals.identify_sets import (
    create_dataframes,
    identify_interval_sets,
)
from graig_nlp.utils import format_duration, time_to_seconds


def format_interval_data(row):
    """
    Formats interval data for display.

    Args:
        row (dict): Row of interval data.

    Returns:
        str: Formatted interval data.
    """
    duration = format_duration(row.get("duration_hms"))
    intensity_label = (
        f" {row.get('intensity_label_v2')}:" if row.get("intensity_label_v2") else " -"
    )
    average_power = f" {row.get('avg_power_w')} W" if row.get("avg_power_w") else ""
    average_cadence = (
        f" - {row.get('avg_cadence_rpm')} rpm" if row.get("avg_cadence_rpm") else ""
    )
    average_torque = (
        f" - {int(row.get('avg_torque_nm'))} Nm"
        if row.get("avg_torque_nm") and row.get("characteristic") == "Torque"
        else ""
    )
    heartrate = (
        f" - {row.get('avg_heartrate_bpm')} bpm"
        if row.get("intensity_label_v2") in ["VO2max", "Threshold", "Tempo", "Aerobic"]
        and row.get("avg_heartrate_bpm")
        else ""
    )

    return f"- {duration}{intensity_label}{average_power}{average_cadence}{average_torque}{heartrate}".strip()


def format_set_data(row):
    """
    Formats set data for display.

    Args:
        row (dict): Row of set data.

    Returns:
        str: Formatted set data.
    """
    intensity_label = (
        f" {row.get('intensity_label_v2')}" if row.get("intensity_label_v2") else ""
    )
    avg_duration = format_duration(row.get("avg_duration_hms"))
    average_power = f" {row.get('avg_power_w')} W" if row.get("avg_power_w") else ""
    average_cadence = (
        f" - {row.get('avg_cadence_rpm')} rpm"
        if isinstance(row.get("avg_cadence_rpm"), int)
        and row.get("avg_cadence_rpm") > 0
        else ""
    )
    average_torque = (
        f" - {row.get('avg_torque_nm')} Nm"
        if row.get("avg_torque_nm") not in ["NA", 0] and intensity_label
        else ""
    )

    return f"{row.get('no_intervals')} x {avg_duration}{intensity_label} efforts:{average_power}{average_cadence}{average_torque}"


def subset_weighted_average(group):
    """
    Calculates weighted averages for a group of intervals.

    Args:
        group (list): List of interval data dictionaries.

    Returns:
        dict: Dictionary containing the weighted averages.
    """
    total_distance = sum(row["distance_km"] for row in group)
    duration_sum = sum(row["duration_hms"] for row in group)
    avg_duration = duration_sum / len(group)
    weighted_avg_power = (
        sum(row["duration_hms"] * row["avg_power_w"] for row in group) / duration_sum
    )
    weighted_avg_speed = total_distance / (duration_sum / 3600)
    weighted_avg_cadence = (
        sum(row["duration_hms"] * row["avg_cadence_rpm"] for row in group)
        / duration_sum
    )
    weighted_avg_heartrate = (
        sum(row["duration_hms"] * row["avg_heartrate_bpm"] for row in group)
        / duration_sum
    )
    weighted_avg_torque = (
        sum(row["duration_hms"] * row["avg_torque_nm"] for row in group) / duration_sum
    )

    return {
        "intensity_label_v2": group[0]["intensity_label_v2"],
        "no_intervals": len(group),
        "total_distance_km": total_distance,
        "total_duration_s": duration_sum,
        "avg_duration_s": avg_duration,
        "avg_power_w": round(weighted_avg_power),
        "avg_torque_nm": round(weighted_avg_torque),
        "avg_speed_kph": round(weighted_avg_speed, 1),
        "avg_cadence_rpm": round(weighted_avg_cadence),
        "avg_heartrate_bpm": round(weighted_avg_heartrate),
    }


def assign_intensity_label_none(grouped_stats):
    """
    Assigns None to the 'intensity_label_v2' field for all rows in each group.

    Args:
        grouped_stats (list): List of grouped statistics.

    Returns:
        list: Updated grouped statistics.
    """
    for group in grouped_stats:
        for row in group:
            row["intensity_label_v2"] = None
    return grouped_stats


def check_and_set_intensity_label(data):
    """
    Checks and sets the intensity label to None if all labels are the same.

    Args:
        data (list): List of interval data dictionaries.

    Returns:
        list: Updated interval data with intensity labels set to None if applicable.
    """
    unique_labels = set(row["intensity_label_v2"] for row in data)
    if len(unique_labels) == 1:
        for row in data:
            row["intensity_label_v2"] = None
    return data


def get_grouped_stats(data):
    """
    Groups interval data by intensity label and calculates weighted averages.

    Args:
        data (list): List of interval data dictionaries.

    Returns:
        list: List of grouped statistics.
    """
    grp_data = copy.deepcopy(data)

    for value in grp_data:
        for key in [
            "distance_km",
            "avg_power_w",
            "avg_speed_kph",
            "avg_cadence_rpm",
            "avg_heartrate_bpm",
            "avg_torque_nm",
        ]:
            value[key] = 0 if value[key] in [None, "NA"] else value[key]

    for row in grp_data:
        row["duration_hms"] = time_to_seconds(row["duration_hms"])

    grouped_data = defaultdict(list)
    for row in grp_data:
        grouped_data[row["intensity_label_v2"]].append(row)

    grouped_stats = [subset_weighted_average(group) for group in grouped_data.values()]

    for entry in grouped_stats:
        entry["total_duration_hms"] = str(
            datetime.timedelta(seconds=int(entry["total_duration_s"]))
        )
        entry["avg_duration_hms"] = str(
            datetime.timedelta(seconds=int(entry["avg_duration_s"]))
        )

    return grouped_stats


def process_intervals(intervals):
    """
    Processes interval data to identify sets and generate formatted statistics.

    Args:
        intervals (list): List of interval data dictionaries.

    Returns:
        list: List of formatted interval statistics.
    """
    # Filter out 'Aerobic' intervals
    intervals_ex_aerobic = [
        entry for entry in intervals if entry["intensity_label_v2"] != "Aerobic"
    ]
    intervals_length = len(intervals_ex_aerobic)

    if intervals_length < 2:
        return []

    # Identify sets and create dataframes
    filtered_intervals, aerobic_indices = identify_interval_sets(intervals)
    separate_sets = [
        df for df in create_dataframes(filtered_intervals, aerobic_indices) if df
    ]

    # Get grouped statistics
    grouped_stats = [get_grouped_stats(s) for s in separate_sets]
    if grouped_stats:
        all_intensity_labels = {
            row["intensity_label_v2"] for group in grouped_stats for row in group
        }
        if len(all_intensity_labels) == 1:
            grouped_stats = assign_intensity_label_none(grouped_stats)

    # Format statistics
    set_stats_text = [
        " & ".join(filter(None, [format_set_data(row) for row in group]))
        for group in grouped_stats
    ]
    separate_sets = [check_and_set_intensity_label(df) for df in separate_sets]
    interval_stats_text = [
        "\n\n".join(filter(None, [format_interval_data(row) for row in df]))
        for df in separate_sets
    ]

    final_interval_stats = []

    if len(interval_stats_text) > 1:
        final_interval_stats = [
            f"Set {i}: {set_stats_text[i-1]}\n\n{text}"
            for i, text in enumerate(interval_stats_text, start=1)
        ]
    else:
        if interval_stats_text:
            final_interval_stats.append(
                f"Session's efforts:\n\n{interval_stats_text[0]}"
            )

    if intervals_length <= 30:
        return final_interval_stats
    else:
        return [
            f"**set {i}**: {text}" for i, text in enumerate(set_stats_text, start=1)
        ]
