import csv
import json
from io import StringIO


class IngestionAgent:
    def normalize(self, content: bytes, content_type: str, filename: str) -> list[dict]:
        if content_type == "text/csv" or filename.lower().endswith(".csv"):
            return list(csv.DictReader(StringIO(content.decode("utf-8"))))

        try:
            parsed = json.loads(content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []
        if isinstance(parsed, list):
            return [event for event in parsed if isinstance(event, dict)]
        if isinstance(parsed, dict):
            records = parsed.get("Records") or parsed.get("events") or parsed.get("findings")
            if isinstance(records, list):
                return [event for event in records if isinstance(event, dict)]
            return [parsed]
        return []
