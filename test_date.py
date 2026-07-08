#!/usr/bin/env -S uv run --script

# ABOUTME: Tests date.py's parsing against log, email, ISO, and prose date
# ABOUTME: formats, asserting the exact UTC instant each input resolves to.

# /// script
# requires-python = ">=3.11"
# dependencies = ["dateparser"]
# ///

import unittest
from datetime import timezone

import date

# (input, expected UTC "YYYY-mm-dd HH:MM:SS")
CASES = [
    # TZ abbreviations that need DST resolved from the date
    ("July 12, 2026 at 11:59:59 PM PT", "2026-07-13 06:59:59"),
    ("Jan 12, 2027 at 11:59:59 PM PT", "2027-01-13 07:59:59"),
    ("July 12, 2026 11:59 PM ET", "2026-07-13 03:59:00"),
    ("Jan 12, 2027 6:00 AM CT", "2027-01-12 12:00:00"),
    ("Dec 3, 2026 4:15 PM MT", "2026-12-03 23:15:00"),
    # TZ abbreviations with fixed offsets
    ("8 July 2026 14:30 BST", "2026-07-08 13:30:00"),
    ("8 July 2026 14:30 CEST", "2026-07-08 12:30:00"),
    ("2026-07-08 14:30 AEST", "2026-07-08 04:30:00"),
    ("Jan 12 2027 6:00 AM CST", "2027-01-12 12:00:00"),
    # Log formats
    ("12/Jul/2026:23:59:59 -0700", "2026-07-13 06:59:59"),
    ("[12/Jul/2026:23:59:59 -0700]", "2026-07-13 06:59:59"),
    ("2026-07-08 14:30:00,123", "2026-07-08 02:30:00"),
    ("2026/07/08 14:30:00", "2026-07-08 02:30:00"),
    ("Mon Jul 12 23:59:59 UTC 2026", "2026-07-12 23:59:59"),
    ("Mon, 12 Jul 2026 23:59:59 +0000", "2026-07-12 23:59:59"),
    ("2026-07-08 14:30:00.123456+12", "2026-07-08 02:30:00"),
    # ISO 8601 variants
    ("2026-07-08T14:30:00.0000000Z", "2026-07-08 14:30:00"),
    ("2026-07-08T14:30:00.123Z", "2026-07-08 14:30:00"),
    ("20260708T143000Z", "2026-07-08 14:30:00"),
    ("2026-07-08T14:30:00+00:00", "2026-07-08 14:30:00"),
    # Unix timestamps
    ("1783296000", "2026-07-06 00:00:00"),
    ("1783296000123", "2026-07-06 00:00:00"),
    # Prose and regional formats
    ("7/12/2026 11:59:59 PM", "2026-07-12 11:59:59"),
    ("12.07.2026 14:30", "2026-07-12 02:30:00"),
    ("08-Jul-2026 14:30:00", "2026-07-08 02:30:00"),
    ("Wednesday, July 8, 2026 2:30:00 PM UTC", "2026-07-08 14:30:00"),
    # Cases carried over from the perl suite (date.t)
    ("26 March 2015 at 06:05 NZDT", "2015-03-25 17:05:00"),
    ("2015-03-25 15:39:54 +0000", "2015-03-25 15:39:54"),
    ("Wed, 25 Mar 2015 14:25:03 -0700 (PDT)", "2015-03-25 21:25:03"),
    ("Wed, 25 Mar 2015 14:25:03 PDT", "2015-03-25 21:25:03"),
    ("Wed, 25 Mar 2015 14:25:03 (PDT)", "2015-03-25 21:25:03"),
    ("Mar 26 9:53 AM 2015 NZDT", "2015-03-25 20:53:00"),
    ("March 26, 2015 at 10:51:30 AM UTC+13", "2015-03-25 21:51:30"),
]


class TestParsing(unittest.TestCase):
    def test_cases(self):
        for s, expected in CASES:
            with self.subTest(input=s):
                dt = date.parse_date(s)
                got = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
