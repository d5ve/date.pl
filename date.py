#!/usr/bin/env -S uv run --script

# ABOUTME: Timezone converter showing local (NZ) time and UTC for a given
# ABOUTME: date/time string, unix timestamp, or relative time expression.

# /// script
# requires-python = ">=3.11"
# dependencies = ["dateparser"]
# ///

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Pacific/Auckland")
UTC = timezone.utc

# Common TZ abbreviations to UTC offset in hours. These abbreviations encode
# their own DST state (PDT vs PST), so a fixed offset is always correct.
# Ambiguous abbreviations (CST, IST) resolve to the American/Indian reading.
TZ_ABBREVS = {
    "NZDT": 13, "NZST": 12,
    "AEDT": 11, "AEST": 10, "ACST": 9.5, "AWST": 8,
    "JST": 9, "IST": 5.5,
    "MSK": 3, "EET": 2, "CET": 1,
    "GMT": 0, "UTC": 0, "WET": 0,
    "BST": 1, "CEST": 2, "EEST": 3,
    "EST": -5, "EDT": -4, "CST": -6, "CDT": -5,
    "MST": -7, "MDT": -6, "PST": -8, "PDT": -7,
    "AKST": -9, "AKDT": -8, "HST": -10,
}

# TZ abbreviations that don't encode DST state (e.g. "11:59 PM PT"). These
# map to IANA zones so the offset resolves correctly for the parsed date.
TZ_ZONES = {
    "PT": "America/Los_Angeles",
    "MT": "America/Denver",
    "CT": "America/Chicago",
    "ET": "America/New_York",
    "AKT": "America/Anchorage",
    "NZT": "Pacific/Auckland",
    "AET": "Australia/Sydney",
}

def clean_date_string(s):
    """Trim and normalise a date string for parsing."""
    s = s.strip()
    s = re.sub(r"\s+at\s+", " ", s)
    s = re.sub(r"[()\[\]]", "", s)
    # Strip ordinal suffixes (1st, 2nd, 3rd, 4th, etc.)
    s = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", s)
    # Apache CLF puts a colon between date and time (12/Jul/2026:23:59:59).
    s = re.sub(r"(\d{2}/[A-Za-z]{3}/\d{4}):", r"\1 ", s)
    # Comma as the fractional-seconds separator (log4j/syslog: 14:30:00,123).
    s = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{1,6})\b", r"\1.\2", s)
    # Normalise UTC+N / UTC-N offsets to +HHMM format.
    s = re.sub(r"UTC([+-])(\d{1,2})$", lambda m: f"{m.group(1)}{int(m.group(2)):02d}00", s)
    # Add space before AM/PM so 12-hour times parse (e.g. "7AM" -> "7 AM").
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
    """Strip a trailing TZ abbreviation and return (cleaned_string, tzinfo_or_None)."""
    m = re.search(r"\s+([A-Z]{2,5})$", s)
    if m:
        abbrev = m.group(1)
        if abbrev in TZ_ABBREVS:
            tz = timezone(timedelta(hours=TZ_ABBREVS[abbrev]))
            return s[:m.start()], tz
        if abbrev in TZ_ZONES:
            return s[:m.start()], ZoneInfo(TZ_ZONES[abbrev])
    return s, None


def parse_iso(s):
    """Try ISO 8601 — handles offsets like +00:00 and compact forms. Returns datetime or None."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def parse_freeform(s):
    """Parse with dateparser, which covers log, email, and prose formats. Returns datetime or None."""
    import dateparser

    settings = {}
    # Dotted dates (12.07.2026) are a European convention, so read them
    # day-first; slash dates keep dateparser's month-first default.
    if re.match(r"\d{1,2}\.\d{1,2}\.\d{2,4}\b", s):
        settings["DATE_ORDER"] = "DMY"
    return dateparser.parse(s, settings=settings)


def parse_datetime_string(s):
    """Parse an absolute date/time string. Returns datetime or None."""
    stripped, tz_override = extract_tz_abbrev(s)
    for parse in (parse_iso, parse_freeform):
        dt = parse(stripped)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz_override or LOCAL_TZ)
            return dt
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


def relative_time(dt):
    """Return a human-friendly string like '3 minutes ago' or '2 hours from now'."""
    now = datetime.now(LOCAL_TZ)
    diff = now - dt
    total_seconds = int(diff.total_seconds())
    future = total_seconds < 0
    total_seconds = abs(total_seconds)

    if total_seconds < 5:
        return "just now"

    minutes = total_seconds / 60
    hours = total_seconds / 3600
    days = total_seconds / 86400
    weeks = days / 7
    months = days / 30.44
    years = days / 365.25

    if minutes < 90:
        value, unit = int(minutes), "minute"
    elif hours < 30:
        value, unit = f"{hours:.1f}", "hour"
    elif days < 14:
        value, unit = f"{days:.1f}", "day"
    elif weeks < 8:
        value, unit = f"{weeks:.1f}", "week"
    elif months < 18:
        value, unit = f"{months:.1f}", "month"
    else:
        value, unit = f"{years:.1f}", "year"

    # Strip trailing .0 for cleaner output
    value = str(value)
    if value.endswith(".0"):
        value = value[:-2]

    if value != "1":
        unit += "s"
    suffix = "from now" if future else "ago"
    return f"{value} {unit} {suffix}"


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
        f"{'':>{tz_width}}  {relative_time(dt)}",
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
