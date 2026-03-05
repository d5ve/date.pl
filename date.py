#!/usr/bin/env python3

# ABOUTME: Timezone converter showing local (NZ) time and UTC for a given
# ABOUTME: date/time string, unix timestamp, or relative time expression.

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Pacific/Auckland")
UTC = timezone.utc

# Common TZ abbreviations to UTC offset in hours. Python's strptime %Z only
# accepts a handful of names, so we map these to numeric offsets ourselves.
TZ_ABBREVS = {
    "NZDT": 13, "NZST": 12,
    "AEDT": 11, "AEST": 10, "ACST": 9.5, "AWST": 8,
    "JST": 9, "CST": 8, "IST": 5.5,
    "MSK": 3, "EET": 2, "CET": 1,
    "GMT": 0, "UTC": 0, "WET": 0,
    "BST": 1, "CEST": 2, "EEST": 3,
    "EST": -5, "EDT": -4, "CST6": -6, "CDT": -5,
    "MST": -7, "MDT": -6, "PST": -8, "PDT": -7,
    "AKST": -9, "AKDT": -8, "HST": -10,
}

# Formats to try when guessing a date string. Order matters — more specific first.
DATE_FORMATS = [
    # ISO-ish
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S %z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    # RFC 2822-ish
    "%a, %d %b %Y %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S",
    # Common log/email formats
    "%d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S",
    "%d %b %Y %H:%M",
    "%b %d %Y %H:%M:%S",
    "%b %d %I:%M %p %Y",
    # Verbose
    "%B %d, %Y %I:%M:%S %p %z",
    "%B %d, %Y %I:%M:%S %p",
    "%B %d, %Y %H:%M:%S",
    "%d %B %Y %H:%M:%S",
    "%d %B %Y %H:%M",
    "%d %B %Y %I %p",
    "%d %B %Y",
    # Date only
    "%d %b %Y",
    "%b %d %Y",
]


def clean_date_string(s):
    """Trim and normalise a date string for parsing."""
    s = s.strip()
    s = re.sub(r"\s+at\s+", " ", s)
    s = re.sub(r"[()]", "", s)
    # Strip ordinal suffixes (1st, 2nd, 3rd, 4th, etc.)
    s = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", s)
    # Normalise UTC+N / UTC-N offsets to +HHMM format.
    s = re.sub(r"UTC([+-])(\d{1,2})$", lambda m: f"{m.group(1)}{int(m.group(2)):02d}00", s)
    # Add space before AM/PM so strptime %I:%M %p works (e.g. "7AM" -> "7 AM").
    s = re.sub(r"(\d)(AM|PM)\b", r"\1 \2", s, flags=re.IGNORECASE)
    # Strip redundant TZ name after a numeric offset (e.g. "-0700 PDT" -> "-0700").
    s = re.sub(r"([+-]\d{4})\s+[A-Z]{2,5}$", r"\1", s)
    return s


def parse_keyword(s):
    """Handle special keywords like 'now', 'today'. Returns datetime or None."""
    if s.lower() in ("now", "today"):
        return datetime.now(LOCAL_TZ)
    return None


def parse_relative(s):
    """Try to parse 'N units ago' expressions. Returns datetime or None."""
    m = re.match(r"(\d+)\s+(minutes?|hours?|days?|weeks?)\s+ago\b", s, re.IGNORECASE)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2).lower().rstrip("s") + "s"
    return datetime.now(LOCAL_TZ) - timedelta(**{unit: n})


def parse_epoch(s):
    """Try to parse unix timestamps (10 or 13 digits). Returns datetime or None."""
    if re.match(r"\d{10}$", s):
        return datetime.fromtimestamp(int(s), tz=LOCAL_TZ)
    if re.match(r"\d{10}\.?\d{3}$", s):
        epoch = int(s[:10])
        return datetime.fromtimestamp(epoch, tz=LOCAL_TZ)
    return None


def extract_tz_abbrev(s):
    """Strip a trailing TZ abbreviation and return (cleaned_string, tz_offset_or_None)."""
    m = re.search(r"\s+([A-Z]{2,5})$", s)
    if m and m.group(1) in TZ_ABBREVS:
        offset_hours = TZ_ABBREVS[m.group(1)]
        tz = timezone(timedelta(hours=offset_hours))
        return s[:m.start()], tz
    return s, None


def parse_datetime_string(s):
    """Try strptime with each candidate format. Returns datetime or None."""
    # First try with the original string (handles %z numeric offsets).
    # Then try with TZ abbreviation stripped and applied manually.
    for stripped, tz_override in [(s, None), extract_tz_abbrev(s)]:
        for fmt in DATE_FORMATS:
            try:
                dt = datetime.strptime(stripped, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=tz_override or LOCAL_TZ)
                return dt
            except ValueError:
                continue
    return None


def parse_date(s):
    """Parse an arbitrary date/time string into a timezone-aware datetime."""
    cleaned = clean_date_string(s)

    # Try each parser in order.
    for parser in (parse_keyword, parse_relative, parse_epoch, parse_datetime_string):
        result = parser(cleaned)
        if result is not None:
            return result

    print(f"Could not parse: {s}", file=sys.stderr)
    sys.exit(1)


def format_output(dt):
    """Format the date in local and UTC as aligned columns."""
    local_dt = dt.astimezone(LOCAL_TZ)
    utc_dt = dt.astimezone(UTC)

    local_name = str(LOCAL_TZ)
    tz_width = max(len(local_name), 3)  # 3 = len("UTC")
    fmt = "%a %Y-%m-%dT%H:%M:%S"

    local_abbr = local_dt.strftime("%Z")
    utc_abbr = utc_dt.strftime("%Z")

    lines = [
        f"{local_name:>{tz_width}}: {local_dt.strftime(fmt)} {local_abbr}",
        f"{'UTC':>{tz_width}}: {utc_dt.strftime(fmt)} {utc_abbr}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Show a date/time in NZ and UTC.",
        epilog=(
            "examples:\n"
            "  date.py                          Current time\n"
            "  date.py 2025-03-06 14:30         Parse a date string\n"
            "  date.py 1427318966               Unix timestamp\n"
            "  date.py 7 hours ago              Relative time\n"
            "  date.py now                      Same as no args\n"
            "  date.py today                    Same as no args\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("date", nargs="*", help="Date/time string to convert")
    args = parser.parse_args()

    if args.date and args.date[0].lower() == "help":
        parser.print_help()
        return

    if args.date:
        dt = parse_date(" ".join(args.date))
    else:
        dt = datetime.now(LOCAL_TZ)

    print(format_output(dt))


if __name__ == "__main__":
    main()
