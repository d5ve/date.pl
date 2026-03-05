# date.py

> Yes, the repo is called `date.pl`. The script used to be Perl. It got better.

A simple timezone converter that shows a date/time in NZ (Pacific/Auckland) and UTC. Useful for marrying up log entry timestamps. Drop it on any machine with Python 3.9+ and run it.

```
$ ./date.py
Pacific/Auckland: Fri 2026-03-06T17:30:00 NZDT
             UTC: Fri 2026-03-06T04:30:00 UTC

$ ./date.py 1427318966
Pacific/Auckland: Thu 2015-03-26T10:29:26 NZDT
             UTC: Wed 2015-03-25T21:29:26 UTC

$ ./date.py 7 hours ago
Pacific/Auckland: Fri 2026-03-06T10:30:00 NZDT
             UTC: Thu 2026-03-05T21:30:00 UTC
```

## Usage

```
date.py                          Current time
date.py now / today              Same as no args
date.py 2025-03-06 14:30         Date string (assumes NZ if no timezone)
date.py 1427318966               Unix timestamp (10 or 13 digits)
date.py 7 hours ago              Relative time
date.py help / --help / -h       Show help
```

## Supported date formats

The parser tries a list of `strptime` patterns and picks the first match. It handles:

- ISO: `2015-03-25 15:39:54 +0000`, `2015-03-25T14:30:00`
- RFC 2822: `Wed, 25 Mar 2015 14:25:03 -0700`
- Verbose: `26 March 2015 at 06:05 NZDT`, `3rd March 2015 at 7AM`
- US-style: `Mar 26 9:53 AM 2015 NZDT`
- Unix epoch: `1427318966`, `1427318966000` (millis truncated)
- Relative: `28 minutes ago`, `7 hours ago`, `3 days ago`

Common timezone abbreviations (NZDT, NZST, BST, PDT, EST, etc.) are recognised and converted to UTC offsets. When no timezone is given, NZ is assumed.

## Requirements

Python 3.9+ (stdlib only — uses `zoneinfo`, no packages to install).

## Legacy

This is a rewrite of [date.pl](date.pl), the original Perl version which also supported a configurable remote timezone for NZ/UK conversions. See [README.pod](README.pod) for its documentation.
