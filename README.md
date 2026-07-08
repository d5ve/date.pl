# date.py

> Yes, the repo is called `date.pl`. The script used to be Perl. It got better.

A simple timezone converter that shows a date/time in NZ (Pacific/Auckland) and UTC. Useful for marrying up log entry timestamps. Drop it on any machine with [uv](https://docs.astral.sh/uv/) and run it — dependencies install themselves on first run.

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

Parsing is handled by [dateparser](https://dateparser.readthedocs.io/) with a normalisation layer in front. It handles:

- ISO 8601 variants: `2015-03-25 15:39:54 +0000`, `2026-07-08T14:30:00.0000000Z`, `20260708T143000Z`
- Log formats: Apache CLF `[12/Jul/2026:23:59:59 -0700]`, log4j `2026-07-08 14:30:00,123`, syslog, `unix date` output
- RFC 2822: `Wed, 25 Mar 2015 14:25:03 -0700`
- Verbose: `26 March 2015 at 06:05 NZDT`, `July 12, 2026 at 11:59:59 PM PT`
- US-style: `7/12/2026 11:59:59 PM`; European dotted dates read day-first: `12.07.2026 14:30`
- Unix epoch: `1427318966`, `1427318966000` (millis truncated)
- Relative: `28 minutes ago`, `7 hours ago`, `3 days ago`

Timezone abbreviations that encode their DST state (NZDT, PDT, BST, etc.) map to fixed offsets. Bare abbreviations (PT, ET, CT, MT) map to IANA zones so the offset is resolved from the date itself. Ambiguous abbreviations get the American/Indian reading (CST is US Central, IST is India). When no timezone is given, NZ is assumed.

## Requirements

[uv](https://docs.astral.sh/uv/) (`brew install uv`). The script declares its own dependencies inline (PEP 723); uv fetches them on first run. Alternatively run with any Python 3.11+ that has `dateparser` installed.

## Tests

```
$ ./test_date.py
```

## Legacy

This is a rewrite of [date.pl](date.pl), the original Perl version which also supported a configurable remote timezone for NZ/UK conversions. See [README.pod](README.pod) for its documentation.
