from datetime import datetime, timedelta

# Define query constants
ACTIVITY_QUERY = """
SELECT
    a.training_stimulus,
    a.timer_time as duration_s,
    a.distance as distance_m,
    a.total_elevation_gain,
    a.average_power * a.timer_time / 1000 as total_work_kj,
    a.average_power,
    a.average_heartrate,
    a.average_speed,
    tp.Title,
    tp.Description,
    JSON_ARRAYAGG(
        JSON_OBJECT(
            "duration_s", l.end - l.start,
            "distance_m", l.distance,
            "intensity_label_v2", l.intensity_v2,
            "characteristic", l.characteristic,
            "average_power", l.power_mean,
            "average_heartrate", l.heart_rate_mean,
            "average_speed", l.speed_mean,
            "average_cadence", l.cadence_mean)) AS intervals
FROM `interface-db-prod-1`.`activities_activitysummary` AS a
INNER JOIN `interface-db-prod-1`.`activities_lap` AS l ON a.id = l.activity_summary_id
LEFT JOIN `interface-db-prod-1`.`activities_trainingpeaksworkout` tp ON tp.activity_summary_id = a.id
LEFT JOIN `interface-db-prod-1`.`profiles_athlete` p ON p.id = a.athlete_id
WHERE a.id = :activity_summary_id
"""

ATHLETE_PROFILE_QUERY = """
SELECT u.first_name, u.last_name, weight, critical_power, athlete_id, activity_date
FROM activities_activitysummary a
JOIN activities_activityraw ar ON ar.activity_summary_id = a.id
LEFT JOIN profiles_athlete p ON p.id = a.athlete_id
LEFT JOIN accounts_useraccount u ON u.id = p.user_id,
LATERAL (
            SELECT m.value as weight
            FROM metrics_metric AS m
            WHERE m.athlete_id = a.athlete_id
            AND m.metric_type = 'WG'
            AND m.unit = 'kg'
            ORDER BY ABS(m.date - a.activity_date)
            LIMIT 1
        ) AS weight,
LATERAL (
            SELECT e.critical_power
            FROM daily_metrics_dailyestimation AS e
            WHERE e.athlete_id = a.athlete_id
            ORDER BY ABS(e.date - a.activity_date)
            LIMIT 1
        ) AS critical_power
WHERE a.id = :activity_summary_id
"""

ACTIVITY_PEAKS_QUERY = """
SELECT rp.duration / 1000000 duration, rp.value as current_value
FROM `interface-db-prod-1`.metrics_recordprofile AS rp
WHERE rp.unit = 'W'
AND rp.relative_work = 0
AND rp.activity_summary_id = :activity_summary_id;
"""

PEAKS_VALUE_QUERY = """
SELECT
    `metrics_recordprofile`.`duration` / 1000000 AS duration,
    MAX(`metrics_recordprofile`.`value`) AS `previous_value`
FROM
    `metrics_recordprofile`
    INNER JOIN `activities_activitysummary` ON (`metrics_recordprofile`.`activity_summary_id` = `activities_activitysummary`.`id`)
WHERE
    DATE(`activities_activitysummary`.`activity_date`) BETWEEN :start_date AND :end_date
    AND `activities_activitysummary`.`athlete_id` = :athlete_id
    AND `metrics_recordprofile`.`relative_work` = 0
    AND `metrics_recordprofile`.`unit` = 'W'
GROUP BY `metrics_recordprofile`.`duration`
"""


def extract_data(activity_id, connection, restrict=None):
    """
    Extracts data for a given activity ID from the database.

    Args:
        activity_id (int): The ID of the activity to extract.
        connection (object): Database connection object.
        restrict (int, optional): Restrict data by team ID.

    Returns:
        tuple: Contains activity details, profile details, activity peaks, and peak values.
    """
    activity_query = ACTIVITY_QUERY
    if restrict:
        activity_query += f" AND p.team_id = {restrict}"

    try:
        activity_details = fetch_activity_details(
            activity_query, connection, activity_id
        )
        if activity_details is None:
            return None, None, None, None

        profile_details = fetch_profile_details(
            ATHLETE_PROFILE_QUERY, connection, activity_id
        )
        activity_peaks = fetch_activity_peaks(
            ACTIVITY_PEAKS_QUERY, connection, activity_id
        )
        peak_values = fetch_peak_values(PEAKS_VALUE_QUERY, connection, profile_details)

        return activity_details, profile_details, activity_peaks, peak_values

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None, None


def fetch_activity_details(query, connection, activity_id):
    """
    Fetches activity details from the database.

    Args:
        query (str): SQL query to execute.
        connection (object): Database connection object.
        activity_id (int): The ID of the activity to fetch.

    Returns:
        DataFrame: Activity details.
    """
    activity_details = connection.query(
        query, params={"activity_summary_id": activity_id}, ttl=600
    )
    if activity_details.iloc[0].isnull().all():
        return None
    return activity_details.to_dict(orient="records")


def fetch_profile_details(query, connection, activity_id):
    """
    Fetches athlete profile details from the database.

    Args:
        query (str): SQL query to execute.
        connection (object): Database connection object.
        activity_id (int): The ID of the activity to fetch.

    Returns:
        dict: Profile details.
    """
    profile_details = connection.query(
        query, params={"activity_summary_id": activity_id}, ttl=600
    )
    return profile_details.to_dict(orient="records")


def fetch_activity_peaks(query, connection, activity_id):
    """
    Fetches activity peaks details from the database.

    Args:
        query (str): SQL query to execute.
        connection (object): Database connection object.
        activity_id (int): The ID of the activity to fetch.

    Returns:
        dict: Activity peaks.
    """
    activity_peaks = connection.query(
        query, params={"activity_summary_id": activity_id}, ttl=600
    )
    return activity_peaks.to_dict(orient="records")


def fetch_peak_values(query, connection, profile_details):
    """
    Fetches peak values from the database within specified date ranges.

    Args:
        query (str): SQL query to execute.
        connection (object): Database connection object.
        profile_details (dict): Profile details containing athlete_id.
        activity_date (datetime): The date of the activity.

    Returns:
        dict: Peak values.
    """
    athlete_id = profile_details[0].get("athlete_id")
    activity_date = profile_details[0].get("activity_date")
    date_ranges = {
        "past_8_weeks_record": activity_date - timedelta(weeks=8),
        "past_year_record": activity_date - timedelta(days=365),
        "all_time_record": datetime(2000, 1, 1),
    }
    end_date = activity_date - timedelta(days=1)
    peak_values = {}

    for key, start_date in date_ranges.items():
        peak_values[key] = connection.query(
            query,
            params={
                "start_date": start_date,
                "end_date": end_date,
                "athlete_id": athlete_id,
            },
            ttl=600,
        ).to_dict(orient="records")

    return peak_values
