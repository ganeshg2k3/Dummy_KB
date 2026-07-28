"""Sample data processing utilities for testing the code knowledge graph scanner."""

import json
import re
from datetime import datetime, timezone


def clean_text(raw_text):
    """Strip whitespace and normalize a raw text string."""
    if raw_text is None:
        return ""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def parse_timestamp(ts_string):
    """Parse an ISO timestamp string into a datetime object."""
    try:
        return datetime.fromisoformat(ts_string.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def validate_record(record):
    """Check that a record dict has the required fields and valid types."""
    required_fields = ["id", "name", "created_at"]
    for field in required_fields:
        if field not in record:
            return False, f"Missing field: {field}"

    if not isinstance(record["id"], (int, str)):
        return False, "id must be int or str"

    cleaned_name = clean_text(record.get("name"))
    if not cleaned_name:
        return False, "name is empty after cleaning"

    parsed_ts = parse_timestamp(record.get("created_at"))
    if parsed_ts is None:
        return False, "created_at is not a valid timestamp"

    return True, "ok"


def process_batch(records):
    """Validate and clean a batch of records, returning valid ones only."""
    valid_records = []
    errors = []

    for record in records:
        is_valid, message = validate_record(record)
        if is_valid:
            record["name"] = clean_text(record["name"])
            valid_records.append(record)
        else:
            errors.append({"record_id": record.get("id"), "error": message})

    return valid_records, errors


def summarize_batch(valid_records, errors):
    """Build a summary dict describing the outcome of process_batch."""
    total = len(valid_records) + len(errors)
    summary = {
        "total_records": total,
        "valid_count": len(valid_records),
        "error_count": len(errors),
        "success_rate": (len(valid_records) / total) if total > 0 else 0.0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return summary


def to_json(obj):
    """Serialize an object to a compact JSON string."""
    return json.dumps(obj, default=str)


def run_pipeline(raw_records):
    """Top-level entry point: process a batch and return a JSON summary."""
    valid_records, errors = process_batch(raw_records)
    summary = summarize_batch(valid_records, errors)
    return to_json({"summary": summary, "valid_records": valid_records, "errors": errors})
