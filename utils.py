from datetime import datetime, timezone

def format_timestamp(timestamp):
    return datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%m/%d %H:%M:%S')

def is_past_timestamp(timestamp):
    timestamp_dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
    current_dt = datetime.now(timezone.utc)
    return timestamp_dt < current_dt
