from datetime import datetime, timedelta, timezone

def create_validity_period(days_valid: int = 30, grace_days: int = 3):
    now = datetime.now(timezone.utc)
    valid_until = now + timedelta(days=days_valid)
    valid_until_with_grace = valid_until + timedelta(days=grace_days)
    return now, valid_until, valid_until_with_grace
