API_URL = "http://localhost:8000"


TEXT = "The UN is said to meet in New-York according to Donald Trump."

ALIASES = {"UN": "ORG_0", "New-York": "LOC_0", "Donald Trump": "PER_0"}

ANONYMIZED_TEXT = "The ORG_0 is said to meet in LOC_0 according to PER_0."

FORMATTED_ALIASES = [
    {"text": k, "alias": v, "alias_type": v.split("_")[0]} for k, v in ALIASES.items()
]
