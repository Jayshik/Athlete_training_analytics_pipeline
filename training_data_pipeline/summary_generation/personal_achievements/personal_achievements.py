from datetime import datetime


# Function to convert seconds to specified format
def format_duration(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = seconds / 60
        if minutes.is_integer():
            return f"{int(minutes)}m"
        else:
            return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        if hours.is_integer():
            return f"{int(hours)}h"
        else:
            return f"{hours:.1f}h"


def create_record_dict(records):
    return {record["duration"]: record["previous_value"] for record in records}


def calculate_percentage_increase(new_value, old_value):
    return ((new_value - old_value) / old_value) * 100


def update_stats(stats, duration, current_value, previous_value):
    percentage_increase = round(
        calculate_percentage_increase(current_value, previous_value), 1
    )
    power_increase = current_value - previous_value
    if current_value > stats["max_value"]:
        stats["max_value"] = current_value
        stats["max_duration"] = format_duration(duration)

    if percentage_increase > stats["max_increase_percentage"]:
        stats["max_increase_percentage"] = percentage_increase

    stats["total_increase_percentage"] += percentage_increase
    stats["count"] += 1
    records = {
        "duration": format_duration(duration),
        "current_value": current_value,
        "previous_value": previous_value,
        "power_increase": power_increase,
        "percentage_increase": percentage_increase,
    }
    stats["broken_records"].append(records)


def generate_record_message(final_stats):
    messages = []
    current_year = datetime.now().year
    periods_order = ["all_time", "past_year", "past_8_weeks"]

    # Updating period names to include current year for past_year
    period_names = {
        "all_time": "All-time",
        "past_year": f"{current_year}",
        "past_8_weeks": "past 8 weeks",
    }

    periods_with_records = [
        period
        for period in periods_order
        if final_stats.get(period, {}).get("count", 0) > 0
    ]

    for period in periods_with_records:
        data = final_stats[period]

        if len(periods_with_records) == 1:
            messages.append(
                f"Congratulations on breaking {data['count']} "
                f"of your {period_names[period]} records!"
            )
            if len(data["broken_records"]) > 1:
                messages.append(
                    f"\nYour {data['max_duration']} performance showed the biggest improvement\n"
                )
        else:
            if periods_with_records.index(period) == 0:
                messages.append(
                    "Congratulations on breaking multiple personal records!"
                )
                messages.append(
                    f"\nYour {data['max_duration']} performance showed the biggest improvement\n"
                )

            messages.append(f"{period_names[period].capitalize()} records:")

        for record in data["broken_records"]:
            messages.append(
                f" - {record['duration']}: {record['current_value']} W "
                f"(+{record['power_increase']} W, {record['percentage_increase']}%)"
            )
        if len(periods_with_records) > 1:
            messages.append("")  # Add a newline for separation

    return "\n".join(messages).strip()


def process_personal_best(activity_peaks, peak_values):
    # Create dictionaries for fast lookup
    past_8_weeks = create_record_dict(peak_values["past_8_weeks_record"])
    past_year = create_record_dict(peak_values["past_year_record"])
    all_time = create_record_dict(peak_values["all_time_record"])

    # Initialize statistics
    stats_template = {
        "count": 0,
        "total_increase_percentage": 0,
        "max_increase_percentage": 0,
        "max_duration": 0,
        "max_value": 0,
    }

    stats = {
        "all_time": {**stats_template, "broken_records": []},
        "past_year": {**stats_template, "broken_records": []},
        "past_8_weeks": {**stats_template, "broken_records": []},
    }

    # Iterate over activity peaks and compare with previous records
    for peak in activity_peaks:
        duration = peak["duration"]
        current_value = peak["current_value"]

        # Check and update all-time records
        if duration in all_time and current_value > all_time[duration]:
            update_stats(stats["all_time"], duration, current_value, all_time[duration])
        # check and update past year records
        elif duration in past_year and current_value > past_year[duration]:
            update_stats(
                stats["past_year"], duration, current_value, past_year[duration]
            )
        # check and update past 8 weeks records
        elif duration in past_8_weeks and current_value > past_8_weeks[duration]:
            update_stats(
                stats["past_8_weeks"], duration, current_value, past_8_weeks[duration]
            )

    # Remove categories with no broken records
    final_stats = {period: data for period, data in stats.items() if data["count"] > 0}

    message = generate_record_message(final_stats)

    return message
