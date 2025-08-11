import json

TEMPLATE = """ Generate a concise text message using the given json input data.
The message should include details of the duration, power, distance, elevation gain and intervals.
The output should be structured in a similar format to the provided examples, without any additional text or explanations"""


EXAMPLES = [
    {
        "input": json.dumps(
            {
                "training_stimulus": "Aerobic",
                "duration_hms": "04:00:00",
                "distance_km": 108,
                "elevation_gain_m": 1081,
                "total_work_kj": 2291,
                "avg_power_w": 159,
                "avg_heartrate_bpm": 125,
                "avg_speed_kph": 27,
                "sets": [
                    {
                        "intensity_label_v2": "Tempo",
                        "no_intervals": 3,
                        "total_duration_hms": "00:47:59",
                        "avg_duration_hms": "00:16:00",
                        "avg_power_w": 281,
                        "avg_torque_nm": "NA",
                        "avg_speed_kph": "NA",
                        "avg_cadence_rpm": 89,
                        "avg_heartrate_bpm": 155,
                    }
                ],
            }
        )
        .replace("{", "{{")
        .replace("}", "}}"),
        "output": (
            "You have completed a 4-hour aerobic ride, covering 108 km with 1,081 m of elevation gain, "
            "at an average of 159 W and 125 bpm. This also includes 3 tempo efforts averaging 281 W over 48 minutes."
        ),
    },
    {
        "input": json.dumps(
            {
                "training_stimulus": "VO2max",
                "duration_hms": "05:07:00",
                "distance_km": 127,
                "elevation_gain_m": 2030,
                "total_work_kj": 2972,
                "avg_power_w": 161,
                "avg_heartrate_bpm": 119,
                "avg_speed_kph": 25,
                "sets": [
                    {
                        "intensity_label_v2": "Threshold",
                        "no_intervals": 8,
                        "total_duration_hms": "00:03:55",
                        "avg_duration_hms": "00:00:29",
                        "avg_power_w": 339,
                        "avg_torque_nm": "NA",
                        "avg_speed_kph": "NA",
                        "avg_cadence_rpm": 85,
                        "avg_heartrate_bpm": 139,
                    },
                    {
                        "intensity_label_v2": "VO2max",
                        "no_intervals": 16,
                        "total_duration_hms": "00:12:12",
                        "avg_duration_hms": "00:00:46",
                        "avg_power_w": 455,
                        "avg_torque_nm": "NA",
                        "avg_speed_kph": "NA",
                        "avg_cadence_rpm": 87,
                        "avg_heartrate_bpm": 157,
                    },
                ],
            }
        )
        .replace("{", "{{")
        .replace("}", "}}"),
        "output": (
            "you've just clocked up a 5h 7min session with VO2max work, 161 W on average, "
            "127 km covered and 2,030 m of positive ascent. You've done 4 minutes at threshold on 8 efforts, "
            "with an average of 339 W and 16 VO2max efforts at an average of 455 W for a total duration of 12 minutes."
        ),
    },
]
