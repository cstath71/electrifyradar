"""Shared helpers for the ElectrifyRadar data pipeline and site build."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"

STATES = {
    "ma": {"name": "Massachusetts", "code": "MA"},
    "me": {"name": "Maine", "code": "ME"},
    "ny": {"name": "New York", "code": "NY"},
    "ca": {"name": "California", "code": "CA"},
    "mn": {"name": "Minnesota", "code": "MN"},
}

LEGAL_SUFFIXES = {
    "inc",
    "incorporated",
    "llc",
    "l l c",
    "co",
    "company",
    "corp",
    "corporation",
    "ltd",
    "limited",
    "plc",
    "pc",
    "pllc",
    "lp",
    "llp",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "listing"


def title_place(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", (value or "").strip())
    if not cleaned:
        return ""
    small = {"of", "and", "the"}
    prefixes = {"st", "st.", "ft", "ft.", "mt", "mt."}
    parts = []
    for word in cleaned.split(" "):
        lower = word.lower()
        if lower in prefixes:
            base = lower[:-1] if lower.endswith(".") else lower
            parts.append(base.capitalize() + ".")
        elif lower in small:
            parts.append(lower)
        elif word.isupper() or word.islower():
            parts.append(word.title())
        else:
            parts.append(word)
    if parts and parts[0] in small:
        parts[0] = parts[0].title()
    return " ".join(parts)


def zip5(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = text.split("-")[0].split(".")[0]
    digits = re.sub(r"\D", "", text)
    if not digits:
        return ""
    return digits.zfill(5)[-5:] if len(digits) >= 5 else digits.zfill(5)


def clean_phone(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    digits = re.sub(r"\D", "", text)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) < 10:
        return ""
    return text


def clean_url(value) -> str:
    if not value:
        return ""
    text = str(value).strip()
    if text.lower() in {"http://", "https://", "http://www.", "https://www.", "n/a", "na", "none", "-"}:
        return ""
    if not re.match(r"^https?://", text, flags=re.I):
        text = "https://" + text.lstrip("/")
    if text.lower() in {"https://", "http://"}:
        return ""
    return text


def normalize_name(value: str) -> str:
    text = (value or "").lower().replace("&", " and ")
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = [tok for tok in text.split() if tok not in LEGAL_SUFFIXES]
    return " ".join(tokens)


def phrase_in_name(name: str, phrase: str) -> bool:
    if not phrase:
        return False
    padded = f" {name} "
    return f" {phrase} " in padded
