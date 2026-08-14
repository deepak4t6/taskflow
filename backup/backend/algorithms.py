"""
Section 2 — Integrated Algorithms Engine: Sorting & Search
"""

def insertion_sort(records: list[dict], key: str) -> None:
    """
    Sorts a list of dictionaries in place by record[key] using insertion sort.
    """
    for i in range(1, len(records)):
        current_record = records[i]
        j = i - 1
        while j >= 0 and records[j][key] > current_record[key]:
            records[j + 1] = records[j]
            j -= 1
        records[j + 1] = current_record


def binary_search(sorted_records: list[dict], target_value: any, key: str) -> int:
    """
    Performs binary search on a list of dictionaries sorted by key.
    Returns the matching index or -1 if not found.
    """
    low = 0
    high = len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_records[mid][key]
        if mid_val == target_value:
            return mid
        elif mid_val < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def linear_search(records: list[dict], target_value: any, key: str) -> int:
    """
    Scans every record in order and returns the first matching index, or -1 if absent.
    """
    for i, record in enumerate(records):
        if record[key] == target_value:
            return i
    return -1


# --- Counting Wrappers for Benchmarking & Testing ---

def insertion_sort_count(records: list[dict], key: str) -> int:
    """
    Sorts records in place using insertion sort and returns the total comparison count as an int.
    """
    comparison_count = 0
    for i in range(1, len(records)):
        current_record = records[i]
        j = i - 1
        while j >= 0:
            comparison_count += 1
            if records[j][key] > current_record[key]:
                records[j + 1] = records[j]
                j -= 1
            else:
                break
        records[j + 1] = current_record
    return comparison_count


def binary_search_count(sorted_records: list[dict], target_value: any, key: str) -> dict:
    """
    Performs binary search on sorted records and returns a dict with 'index' and 'comparison_count'.
    """
    low = 0
    high = len(sorted_records) - 1
    comparison_count = 0
    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_records[mid][key]
        comparison_count += 1
        if mid_val == target_value:
            return {"index": mid, "comparison_count": comparison_count}
        elif mid_val < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return {"index": -1, "comparison_count": comparison_count}


def linear_search_count(records: list[dict], target_value: any, key: str) -> dict:
    """
    Performs linear search and returns a dict with 'index' and 'comparison_count'.
    """
    comparison_count = 0
    for i, record in enumerate(records):
        comparison_count += 1
        if record[key] == target_value:
            return {"index": i, "comparison_count": comparison_count}
    return {"index": -1, "comparison_count": comparison_count}
