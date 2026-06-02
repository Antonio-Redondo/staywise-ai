import re
from typing import List
from app.models.intent import Intent


def parse_intent(text: str) -> Intent:
    """Lightweight intent parser used in tests and as a fallback when LLM
    access is unavailable. Extracts simple budget and bedroom ranges and a
    couple of lifestyle tags heuristically.
    """
    text_l = text.lower()
    # budgets: find dollar amounts like $1,200,000 or 1200000
    dollars = re.findall(r"\$?([0-9,]{3,})", text)
    nums = [int(d.replace(",", "")) for d in dollars] if dollars else []
    budget_min = None
    budget_max = None
    if len(nums) == 1:
        budget_max = nums[0]
        budget_min = int(nums[0] * 0.8)
    elif len(nums) >= 2:
        budget_min = min(nums)
        budget_max = max(nums)

    # bedrooms: look for '2 bed' or '2-bedroom' patterns
    beds = re.findall(r"(\d+)\s*(?:bed|br)\b", text_l)
    beds_nums = [int(b) for b in beds] if beds else []
    bedrooms_min = None
    bedrooms_max = None
    if beds_nums:
        bedrooms_min = min(beds_nums)
        bedrooms_max = max(beds_nums)

    tags: List[str] = []
    if "bart" in text_l:
        tags.append("near_bart")
    if "walk" in text_l or "walkable" in text_l:
        tags.append("walkable")

    return Intent(
        budget_min=budget_min,
        budget_max=budget_max,
        bedrooms_min=bedrooms_min,
        bedrooms_max=bedrooms_max,
        lifestyle_tags=tags,
    )
