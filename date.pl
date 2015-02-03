#!/usr/bin/perl

use warnings;
use strict;

use DateTime::Format::DateParse;

my $date_str = join ' ', @ARGV;

print "FROM: $date_str\n";

my $dt = DateTime::Format::DateParse->parse_datetime($date_str);

print "PARSED: $dt\n";

$dt->set_time_zone('GMT');

print "GMT: $dt\n";

