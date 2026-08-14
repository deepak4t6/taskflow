import sys
import os
import json
import random

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from algorithms import (
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
    insertion_sort,
)


def generate_task_dataset(n: int) -> list[dict]:
    priorities = ["low", "medium", "high"]
    priority_rank_map = {"low": 1, "medium": 2, "high": 3}
    due_dates = ["today", "tomorrow", "next monday", "next friday", "2026-08-15", None]

    dataset = []
    for i in range(1, n + 1):
        p = random.choice(priorities)
        t = {
            "id": i,
            "title": f"Task_{i:05d}_Title",
            "priority": p,
            "priority_rank": priority_rank_map[p],
            "due_date": random.choice(due_dates) or "",
            "project_id": (i % 5) + 1,
        }
        dataset.append(t)
    return dataset


def run_benchmark():
    sizes = [10, 500, 3000]
    results = {}

    print("=== TaskFlow Algorithms Benchmark Runner ===")

    for n in sizes:
        print(f"\n--- Testing Size N = {n} ---")
        raw_data = generate_task_dataset(n)

        # 1. Insertion Sort by priority_rank
        sort_data = [dict(d) for d in raw_data]
        sort_comparisons = insertion_sort_count(sort_data, key="priority_rank")
        print(f"Insertion Sort Comparisons (Priority Rank): {sort_comparisons:,}")

        # 2. Binary Search vs Linear Search (Target Present at end of list)
        # Prepare title index sorted by title
        indexed_data = [{"id": d["id"], "title": d["title"]} for d in raw_data]
        insertion_sort(indexed_data, key="title")

        target_title_present = indexed_data[-1]["title"]
        target_title_absent = "Task_99999_NonExistent"

        bin_present = binary_search_count(indexed_data, target_title_present, key="title")
        lin_present = linear_search_count(indexed_data, target_title_present, key="title")

        bin_absent = binary_search_count(indexed_data, target_title_absent, key="title")
        lin_absent = linear_search_count(indexed_data, target_title_absent, key="title")

        print(f"Binary Search (Present): Index={bin_present['index']}, Comparisons={bin_present['comparison_count']}")
        print(f"Linear Search (Present): Index={lin_present['index']}, Comparisons={lin_present['comparison_count']}")

        print(f"Binary Search (Absent): Index={bin_absent['index']}, Comparisons={bin_absent['comparison_count']}")
        print(f"Linear Search (Absent): Index={lin_absent['index']}, Comparisons={lin_absent['comparison_count']}")

        results[str(n)] = {
            "size": n,
            "insertion_sort_comparisons": sort_comparisons,
            "binary_search_present_comparisons": bin_present["comparison_count"],
            "linear_search_present_comparisons": lin_present["comparison_count"],
            "binary_search_absent_comparisons": bin_absent["comparison_count"],
            "linear_search_absent_comparisons": lin_absent["comparison_count"],
        }

    # Save benchmark results to JSON file
    out_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved raw benchmark counts to {out_path}")
    return results


if __name__ == "__main__":
    run_benchmark()
