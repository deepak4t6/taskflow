import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)


def run_case(case_name, actual, expected):
    if actual == expected:
        print(f"PASS: {case_name}")
        return True
    else:
        print(f"FAIL: {case_name} — expected {expected}, got {actual}")
        return False


def main():
    print("--- Running Section 2 Algorithm Verification Checks ---")

    # Case 1: insertion_sort on empty list
    empty_list = []
    insertion_sort(empty_list, key="val")
    run_case("insertion_sort on empty list", empty_list, [])

    # Case 2: insertion_sort on single-element list
    single_item = [{"val": 42}]
    insertion_sort(single_item, key="val")
    run_case("insertion_sort on single-element list", single_item, [{"val": 42}])

    # Case 3: binary_search at first, last, and middle index
    sorted_sample = [
        {"val": 10},
        {"val": 20},
        {"val": 30},
        {"val": 40},
        {"val": 50},
    ]
    idx_first = binary_search(sorted_sample, 10, key="val")
    idx_mid = binary_search(sorted_sample, 30, key="val")
    idx_last = binary_search(sorted_sample, 50, key="val")

    bsearch_pass = (idx_first == 0) and (idx_mid == 2) and (idx_last == 4)
    run_case("binary_search at first, middle, and last indices", bsearch_pass, True)

    # Case 4: binary_search returns not-found (-1) for absent target
    idx_absent = binary_search(sorted_sample, 999, key="val")
    run_case("binary_search absent target", idx_absent, -1)

    # Case 5: insertion_sort_count sorts list correctly and returns int > 0
    unsorted_sample = [{"val": 5}, {"val": 1}, {"val": 3}]
    cmp_count = insertion_sort_count(unsorted_sample, key="val")
    is_sorted = unsorted_sample == [{"val": 1}, {"val": 3}, {"val": 5}]
    is_int_gt_zero = type(cmp_count) == int and cmp_count > 0
    run_case("insertion_sort_count output structure and mutation", is_sorted and is_int_gt_zero, True)

    # Case 6: binary_search_count returns dict with correct index and comparison_count > 0
    bsearch_cnt_res = binary_search_count(sorted_sample, 30, key="val")
    bsearch_cnt_valid = (
        isinstance(bsearch_cnt_res, dict)
        and bsearch_cnt_res.get("index") == 2
        and isinstance(bsearch_cnt_res.get("comparison_count"), int)
        and bsearch_cnt_res.get("comparison_count") > 0
    )
    run_case("binary_search_count structure and count", bsearch_cnt_valid, True)

    # Case 7: linear_search_count for absent value returns index -1 and comparison_count == len(list)
    lsearch_cnt_res = linear_search_count(sorted_sample, 999, key="val")
    lsearch_valid = (
        isinstance(lsearch_cnt_res, dict)
        and lsearch_cnt_res.get("index") == -1
        and lsearch_cnt_res.get("comparison_count") == len(sorted_sample)
    )
    run_case("linear_search_count absent target", lsearch_valid, True)


if __name__ == "__main__":
    main()
