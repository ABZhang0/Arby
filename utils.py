from datetime import datetime, timezone

def format_timestamp(timestamp):
    return datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%m/%d/%Y %H:%M')
