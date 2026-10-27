from datetime import datetime, timezone


def utcnow():
    # naive UTC, keeps the format already stored in the database
    return datetime.now(timezone.utc).replace(tzinfo=None)
