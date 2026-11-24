from datetime import date, timedelta

DAY_CODES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def make_occurrence(event, on_date):
    """Copy an event and set the specific date it happens on."""
    occurrence = dict(event)
    occurrence["date"] = on_date
    return occurrence


def expand_event(event, range_start, range_end):
    """Return every occurrence of an event between range_start and range_end (inclusive)."""
    first = date.fromisoformat(event["date"])

    # One-time event: include it only if it falls in the range
    if not event["repeat_days"]:
        if range_start <= first <= range_end:
            return [make_occurrence(event, first)]
        return []

    # Repeating event: walk through each day and keep the matching weekdays
    repeat_days = event["repeat_days"].split(",")
    last = date.fromisoformat(event["repeat_until"]) if event["repeat_until"] else range_end

    current = max(first, range_start)
    end = min(last, range_end)
    occurrences = []
    while current <= end:
        if DAY_CODES[current.weekday()] in repeat_days:
            occurrences.append(make_occurrence(event, current))
        current += timedelta(days=1)
    return occurrences


def occurrences_between(events, range_start, range_end):
    """Expand all events and return their occurrences sorted by date and time."""
    result = []
    for event in events:
        result.extend(expand_event(event, range_start, range_end))
    result.sort(key=lambda o: (o["date"], o["start_time"] or ""))
    return result


def countdown(on_date, today):
    """Human-friendly text like 'today', 'tomorrow', 'in 3 days', 'overdue by 2 days'."""
    days = (on_date - today).days
    if days < 0:
        return f"overdue by {-days} day{'s' if days != -1 else ''}"
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    return f"in {days} days"