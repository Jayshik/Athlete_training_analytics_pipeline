import datetime
import time

import streamlit as st

from graig_nlp.summary_generation.intervals.process_details_intervals import (
    get_grouped_stats,
)

# Define constants
TRAINING_STIMULI = {
    "N": "Neuromuscular",
    "AN": "Anaerobic",
    "V": "VO2max",
    "T": "Threshold",
    "A": "Aerobic",
    "RV": "Recovery",
    "LC": "Lactate Clearance",
    "FR": "Fatigue Resistance",
    "AV": "Activation",
    "TS": "Test",
    "R": "Race",
}

INTENSITY_V2 = {
    "A": "Aerobic",
    "T": "Threshold",
    "V": "VO2max",
    "AN": "Anaerobic",
    "N": "Neuromuscular",
    "TP": "Tempo",
}

CHARACTERISTICS = {
    "M": "Maximum",
    "T": "Torque",
    "C": "Cadence",
    # "P": "Progressive",
    "R": "Intra-Recovery",
    "D": "Dynamic",
}


def format_session_data(session_data):
    """
    Formats session data for display.

    Args:
        session_data (dict): Raw session data.

    Returns:
        dict: Formatted session data.
    """
    session_data = {
        key: value if value is not None else "NA" for key, value in session_data.items()
    }
    session_data["duration_s"] = time.strftime(
        "%H:%M:%S", time.gmtime(session_data["duration_s"])
    )
    if isinstance(session_data["distance_m"], (int, float)):
        session_data["distance_m"] = round(session_data["distance_m"] / 1000, 1)
    if isinstance(session_data["average_speed"], (int, float)):
        session_data["average_speed"] = round(session_data["average_speed"] * 3.6, 1)

    renamed_columns = {
        "duration_s": "duration_hms",
        "distance_m": "distance_km",
        "average_power": "avg_power_w",
        "average_speed": "avg_speed_kph",
        "average_cadence": "avg_cadence_rpm",
        "average_heartrate": "avg_heartrate_bpm",
        "total_elevation_gain": "elevation_gain_m",
    }
    session_data = {renamed_columns.get(k, k): v for k, v in session_data.items()}

    for key, value in session_data.items():
        if key not in {"distance_km", "avg_speed_kph"} and isinstance(
            value, (int, float)
        ):
            session_data[key] = round(value)

    session_data["training_stimulus"] = TRAINING_STIMULI.get(
        session_data.get("training_stimulus"), "NA"
    )
    return session_data


def format_interval_data(interval_data):
    """
    Formats interval data for display.

    Args:
        interval_data (list): List of raw interval data.

    Returns:
        list: Formatted interval data.
    """
    formatted_intervals = []
    for interval in interval_data:
        formatted_interval = {}
        formatted_interval["distance_km"] = (
            round(interval["distance_m"] / 1000, 1)
            if isinstance(interval["distance_m"], (int, float))
            else "NA"
        )
        formatted_interval["duration_hms"] = str(
            datetime.timedelta(seconds=int(interval["duration_s"]))
        )
        formatted_interval["avg_speed_kph"] = (
            round(interval["average_speed"] * 3.6, 1)
            if interval["average_speed"] not in [None, 0]
            else "NA"
        )
        formatted_interval["avg_power_w"] = interval.pop("average_power", 0)
        formatted_interval["avg_cadence_rpm"] = interval.pop("average_cadence", 0)
        formatted_interval["avg_heartrate_bpm"] = interval.pop("average_heartrate", 0)
        if formatted_interval["avg_cadence_rpm"]:
            formatted_interval["avg_torque_nm"] = round(
                (formatted_interval["avg_power_w"] * 60)
                / (formatted_interval["avg_cadence_rpm"] * 2 * 3.14),
                0,
            )
        else:
            formatted_interval["avg_torque_nm"] = None

        formatted_interval["characteristic"] = CHARACTERISTICS.get(
            interval["characteristic"]
        )
        formatted_interval["intensity_label_v2"] = INTENSITY_V2.get(
            interval["intensity_label_v2"]
        )
        if formatted_interval["characteristic"] == "Maximum":
            formatted_interval["intensity_label_v2"] = "Maximum"

        formatted_intervals.append(formatted_interval)

    desired_order = [
        "intensity_label_v2",
        "distance_km",
        "duration_hms",
        "avg_power_w",
        "avg_torque_nm",
        "avg_heartrate_bpm",
        "avg_cadence_rpm",
        "avg_speed_kph",
        "characteristic",
    ]
    result = [
        {key: interval[key] for key in desired_order}
        for interval in formatted_intervals
    ]

    return result


def format_set_data(sets_data):
    """
    Formats set data for display.

    Args:
        sets_data (list): List of set data.

    Returns:
        list: Formatted set data.
    """
    all_aerobic = all(entry["intensity_label_v2"] == "Aerobic" for entry in sets_data)
    filtered_data = (
        []
        if all_aerobic
        else [entry for entry in sets_data if entry["intensity_label_v2"] != "Aerobic"]
    )
    set_stats = get_grouped_stats(filtered_data)

    desired_order = [
        "intensity_label_v2",
        "no_intervals",
        "total_distance_km",
        "total_duration_hms",
        "avg_duration_hms",
        "avg_power_w",
        "avg_torque_nm",
        "avg_heartrate_bpm",
        "avg_cadence_rpm",
        "avg_speed_kph",
    ]
    set_df = [{key: sets[key] for key in desired_order} for sets in set_stats]

    return set_df


def display_table_details(title, description, session_df, sets_df, intervals_df):
    """
    Displays session, set, and interval details in a tabbed format.

    Args:
        title (str): Title of the session.
        description (str): Description of the session.
        session_df (dict): Formatted session data.
        sets_df (list): Formatted set data.
        intervals_df (list): Formatted interval data.
    """
    if intervals_df is not None:
        tab1, tab2, tab3 = st.tabs(["Session", "Intensities", "Intervals"])
        with tab1:
            st.markdown(f"**Title:** {title}")
            st.markdown(f"**Description:** {description}")
            st.dataframe([session_df], hide_index=True)
        with tab2:
            if sets_df:
                st.dataframe(sets_df, hide_index=True)
            else:
                st.markdown("**No sets available!**")
        with tab3:
            st.dataframe(intervals_df)
    else:
        st.markdown(f"**Title:** {title}")
        st.markdown(f"**Description:** {description}")
        st.dataframe(session_df, hide_index=True)
