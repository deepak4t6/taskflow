import os
import re
from typing import Optional, Dict, Any

SYSTEM_PROMPT = """You are an AI task parsing assistant. Your task is to extract structured task information from a plain English description.
Output a JSON object with:
- title: concise title of the task (string)
- priority: "high", "medium", or "low"
- due_date_hint: parsed due date phrase (e.g. "tomorrow", "next friday") or null if not present.
"""

PRIORITY_GROUP_1 = ["urgent", "asap"]
PRIORITY_GROUP_2 = ["whenever", "low priority"]
ALL_PRIORITY_KEYWORDS = ["urgent", "asap", "whenever", "low priority"]

DATE_PHRASES = [
    "today",
    "tomorrow",
    "next week",
    "next monday",
    "next tuesday",
    "next wednesday",
    "next thursday",
    "next friday",
    "next saturday",
    "next sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def parse_task_description_mock(description: str) -> Dict[str, Any]:
    """
    Deterministic, rule-based mock parser following Section 3 Task 3 algorithm:
    a. Lower-cased working copy for keyword matching.
    b. Priority determination:
       - (i) contains "urgent" or "asap" -> "high"
       - (ii) contains "whenever" or "low priority" -> "low"
       - (iii) neither -> "medium"
    c. Due-date hint extraction.
    d. Title derivation by removing priority keywords and matched date phrase, fallback to "Untitled task".
    """
    if description is None:
        description = ""

    lower_desc = description.lower()

    # Step b: Priority
    has_g1 = any(kw in lower_desc for kw in PRIORITY_GROUP_1)
    has_g2 = any(kw in lower_desc for kw in PRIORITY_GROUP_2)

    if has_g1:
        priority = "high"
    elif has_g2:
        priority = "low"
    else:
        priority = "medium"

    # Step c: Due-date hint
    matched_date_phrase: Optional[str] = None
    for phrase in DATE_PHRASES:
        if phrase in lower_desc:
            matched_date_phrase = phrase
            break

    due_date_hint = matched_date_phrase.lower() if matched_date_phrase else None

    # Step d: Title derivation
    title_text = description

    # Keywords to strip from title
    keywords_to_strip = list(ALL_PRIORITY_KEYWORDS)
    if matched_date_phrase:
        keywords_to_strip.append(matched_date_phrase)

    # Sort keywords by length descending so longer phrases (e.g. "next friday") are stripped before shorter sub-parts
    keywords_to_strip.sort(key=len, reverse=True)

    for kw in keywords_to_strip:
        if kw.lower() in lower_desc:
            pattern = re.escape(kw)
            title_text = re.sub(pattern, "", title_text, flags=re.IGNORECASE)

    title = title_text.strip()
    if not title:
        title = "Untitled task"

    return {
        "title": title,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }


def parse_task_description(description: str) -> Dict[str, Any]:
    """
    Main parser entrypoint. Supports optional real LLM via USE_REAL_LLM env var,
    falling back to deterministic mock if disabled or missing API key.
    """
    use_real_llm = os.environ.get("USE_REAL_LLM", "false").lower() == "true"
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if use_real_llm and api_key:
        # Structured message role prompt format
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": description},
        ]
        # In a real environment with API key, call LLM provider here.
        # Fall back to mock if call fails or not enabled.
        pass

    return parse_task_description_mock(description)
