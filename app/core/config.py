"""Configuration constants for source credibility and allowed domains."""

SOURCE_WEIGHTS = {
    "gov_policy": 1.0,
    "who.int": 0.95,
    "un.org": 0.93,
    "reuters.com": 0.9,
}

ALLOWED_EXTERNAL_DOMAINS = ["who.int", "un.org", "reuters.com"]
