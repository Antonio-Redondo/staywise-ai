import re
from typing import List
from app.models.intent import Intent

# Preference keywords -> lifestyle tag. These influence ranking (see rank_listings).
_PREFERENCE_KEYWORDS = {
    "walkable": ["walk", "walkable"],
    "transit": ["transit", "bart", "subway", "train", "metro", "commute"],
    "quiet": ["quiet", "quieter", "peaceful", "calm", "residential"],
    "spacious": ["spacious", "bigger", "larger", "large", "roomy", "more space"],
    "cheaper": ["cheap", "cheaper", "affordable", "lower price", "save money"],
    "premium": ["premium", "luxury", "luxurious", "high-end", "upscale", "more expensive"],
}

# Amenity keywords -> required amenity (must_have). Boosts listings that have them.
_AMENITY_KEYWORDS = {
    "parking": ["parking", "garage"],
    "pet_friendly": ["pet", "pets", "dog", "cat"],
    "in_unit_laundry": ["laundry", "washer", "dryer"],
    "gym": ["gym", "fitness"],
    "pool": ["pool"],
}


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
    beds = re.findall(r"(\d+)\s*(?:bedrooms|bedroom|beds|bed|br)\b", text_l)
    beds_nums = [int(b) for b in beds] if beds else []
    bedrooms_min = None
    bedrooms_max = None
    if beds_nums:
        bedrooms_min = min(beds_nums)
        bedrooms_max = max(beds_nums)

    tags: List[str] = []
    if "bart" in text_l:
        tags.append("near_bart")
    for tag, keywords in _PREFERENCE_KEYWORDS.items():
        if any(kw in text_l for kw in keywords):
            tags.append(tag)
    tags = list(dict.fromkeys(tags))  # dedupe, preserve order

    must_haves: List[str] = []
    for amenity, keywords in _AMENITY_KEYWORDS.items():
        if any(kw in text_l for kw in keywords):
            must_haves.append(amenity)

    return Intent(
        budget_min=budget_min,
        budget_max=budget_max,
        bedrooms_min=bedrooms_min,
        bedrooms_max=bedrooms_max,
        lifestyle_tags=tags,
        must_haves=must_haves,
    )
