#!/usr/bin/perl

use warnings;
use strict;

my $VERSION = '0.9';

=head1 date.pl - Perl timezone converter script

Convert NZ time strings to GMT and vice-versa.

=head1 SYNOPSIS

    # Convert NZ datetime to GMT
    $ date.pl Tue Feb 03 07:00 NZDT 2015
    $ date.pl Tue Feb 03 07:00 GMT+1300 2015
    GMT: 2015-02-02T18:00:00
    
    # Convert GMT datetime to NZT
    $ date.pl 2015-01-17 13:24:00 GMT
    GMT: 2015-01-17T00:24:00
    
=head1 INSTALLATION

Simply copy the B<date.pl> script to a directory in your $PATH.
 
=head1 DEPENDENCIES

This module requires these other modules and libraries:

=over

=item * L<DateTime::Format::DateParse>

=item * L<Date::Parse>

=back

=cut

use DateTime::Format::DateParse;

my $date_str = join ' ', @ARGV;

$date_str or die "USAGE: $0 <date string>";

#print "FROM: $date_str\n";

my $local_dt = DateTime->now(time_zone => 'Pacific/Auckland');
my $remote_dt = DateTime->now(time_zone => 'Europe/London');

# This defaults to the local TZ if the string contains no hint.
my $parsed_dt = DateTime::Format::DateParse->parse_datetime($date_str);
my $parsed_tz = $parsed_dt->time_zone_short_name;

#print "PARSED: $parsed_dt $parsed_tz\n";

# Behaviour - do any of the following which match.
# If the input datetime isn't in the local timezone, then convert it to local.
# If the input datetime isn't in the remote timezone, then convert it to remote.

if ( $parsed_dt ne $local_dt->time_zone_short_name ) {
    $parsed_dt->set_time_zone($local_dt->time_zone_long_name);
    print $local_dt->time_zone_long_name . ": $parsed_dt " . $parsed_dt->time_zone_short_name . "\n";
}

if ( $parsed_dt ne $remote_dt->time_zone_short_name ) {
    $parsed_dt->set_time_zone($remote_dt->time_zone_long_name);
    print $remote_dt->time_zone_long_name . ": $parsed_dt " . $parsed_dt->time_zone_short_name . "\n";
}

exit;

__END__

=head1 LICENCE

Copyright 2015 Dave Webb

date.pl is free software. You can do B<anything> you like with it.

=head1 CHANGES

=over

=item * 2015-02-09 - VERSION 0.9

First release. Basic but working.

=cut
