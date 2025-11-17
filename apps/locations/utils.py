from rapidfuzz import fuzz
from .models import Location


def find_best_matching_location(address_text: str, threshold=80):
    """
    Returns best matching Location object using fuzzy matching.
    If no match >= threshold → returns None.
    """
    if not address_text:
        return None

    address_text = address_text.lower().strip()

    best_location = None
    highest_score = 0

    # Search in all saved locations
    for loc in Location.objects.all():
        compare_text = f"{loc.street_address} {loc.city} {loc.state} {loc.pincode}".lower()

        score = fuzz.token_set_ratio(address_text, compare_text)

        if score > highest_score:
            highest_score = score
            best_location = loc

    return best_location if highest_score >= threshold else None
