def min_to_24(minutes: int) -> str:
    """Convert minutes (0–1440) to 24-hour time string 'HH:MM'."""
    if not (0 <= minutes <= 1440):
        raise ValueError("Minutes must be between 0 and 1440")
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"

def time24_to_min(time_str: str) -> int:
    try:
        hours, mins = map(int, time_str.split(':'))
        if not (0 <= hours < 24 and 0 <= mins < 60):
            raise ValueError
    except ValueError:
        raise ValueError('Time must be in "HH:MM" 24-hour format')
    return hours * 60 + mins