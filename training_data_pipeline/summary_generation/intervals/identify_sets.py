def identify_interval_sets(intervals):
    """
    Identifies and filters interval sets based on specific criteria.

    Args:
        intervals (list): List of interval data dictionaries.

    Returns:
        tuple: Filtered intervals and new aerobic indices.
    """
    # Filter out intervals where intensity is 'Aerobic' and characteristic is 'Intra-Recovery'
    filtered_intervals = [
        interval
        for interval in intervals
        if not (
            interval.get("intensity_label_v2") == "Aerobic"
            and interval.get("characteristic") == "Intra-Recovery"
        )
    ]

    # Identify indices of 'Aerobic' intervals
    aerobic_indices = [
        i
        for i, interval in enumerate(filtered_intervals)
        if interval.get("intensity_label_v2") == "Aerobic"
    ]

    # Compute indices to remove based on consecutive 'Aerobic' intervals
    indices_to_remove = []
    if len(aerobic_indices) > 2:
        for i in range(1, len(aerobic_indices) - 1):
            if (aerobic_indices[i] - aerobic_indices[i - 1] == 2) and (
                aerobic_indices[i + 1] - aerobic_indices[i] == 2
            ):
                indices_to_remove.append(aerobic_indices[i])

    # Filter out the identified indices
    filtered_intervals = [
        interval
        for i, interval in enumerate(filtered_intervals)
        if i not in indices_to_remove
    ]

    # Update 'Aerobic' indices in the filtered intervals
    new_aerobic_indices = [
        i
        for i, interval in enumerate(filtered_intervals)
        if interval.get("intensity_label_v2") == "Aerobic"
    ]

    return filtered_intervals, new_aerobic_indices


def create_dataframes(data, index_list):
    """
    Creates dataframes (segments) by splitting the data based on provided indices.

    Args:
        data (list): List of data to split.
        index_list (list): List of indices to split the data.

    Returns:
        list: List of dataframes (segments).
    """
    if not index_list:
        return [
            data
        ]  # If no indices are provided, return the original data as a single segment.

    # Split the data into segments based on the provided indices.
    dataframes = [
        data[index_list[i] + 1 : index_list[i + 1]] for i in range(len(index_list) - 1)
    ]

    # Handle the segment after the last index in the index_list.
    if index_list and index_list[-1] < len(data) - 1:
        dataframes.append(data[index_list[-1] + 1 :])

    return dataframes
