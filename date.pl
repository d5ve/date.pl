#!/usr/bin/perl

package Date;

use warnings;
use strict;

our $VERSION = '1.00';

=head1 date.pl - Perl timezone converter script

Convert NZ-time strings to UK-time and vice-versa.

=head1 SYNOPSIS

    # Just show current time locally, and remotely (and in UTC if remote isn't
    # currently that).
    $ date.pl
    Pacific/Auckland: Thu 2015-09-24T21:47:50 NZST
       Europe/London: Thu 2015-09-24T10:47:50 BST
                 UTC: Thu 2015-09-24T09:47:50 UTC

    # Parse common date formats
    $ date.pl Tue Feb 03 07:00 NZDT 2015
    $ date.pl 3rd March 2015 at 7AM
    $ date.pl 2015-02-03 07:00:00
    Pacific/Auckland: Tue 2015-02-03T07:00:00 NZDT
       Europe/London: Mon 2015-02-02T18:00:00 GMT
                 UTC: Mon 2015-02-02T18:00:00 UTC

    # Parse a unix epoch timestamp.
    $ date.pl 1427318966
    Pacific/Auckland: Thu 2015-03-26T10:29:26 NZDT
       Europe/London: Wed 2015-03-25T21:29:26 GMT
                 UTC: Wed 2015-03-25T21:29:26 UTC

    # Parse simple N $units ago
    $ date.pl 7 hours ago
    Pacific/Auckland: Sat 2017-05-06T02:23:46 NZST
       Europe/London: Fri 2017-05-05T15:23:46 BST
                 UTC: Fri 2017-05-05T14:23:46 UTC

=head1 INSTALLATION

Simply copy the B<date.pl> script to a directory in your $PATH.
 
=head1 DEPENDENCIES

This module requires these other modules and libraries:

=over

=item * L<DateTime::Format::DateParse>

=item * L<Date::Parse>

=item * L<List::Util>

=back

=cut

use Data::Dumper;
use DateTime::Format::DateParse;
use List::Util ();

use constant {
    local_tz  => 'Pacific/Auckland',
    remote_tz => 'Europe/London',
};

__PACKAGE__->run(join ' ', @ARGV) unless caller();

sub run {
    my $class = shift;
    my $date_str = shift || DateTime->now( time_zone => local_tz() );

    my $date = $class->new( date_str => $date_str );

    #print "FROM:   $date->{clean_date_str}\n";
    #print "PARSED: $date->{parsed_dt} $date->{parsed_tz}\n";
    my $tz_len = List::Util::max map {length} ( $date->{local_dt}->time_zone_long_name, $date->{remote_dt}->time_zone_long_name );
    my $format = "%${tz_len}s: %s %-4s %s\n";
    for my $t (qw( local remote utc )) {
        printf $format, 
            $date->{ $t . '_parsed_dt' }->time_zone_long_name,
            $date->{ $t . '_parsed_dt' }->day_abbr,
            $date->{ $t . '_parsed_dt' },
            $date->{ $t . '_parsed_dt' }->time_zone_short_name,
            ;
    }
}

sub new {
    my $class = shift;
    my %args  = @_;

    die "FATAL new() needs date_str arg" unless $args{date_str};

    my $self = {
        date_str  => $args{date_str},
        local_dt  => DateTime->now( time_zone => ( $args{local_tz} || local_tz() ) ),
        remote_dt => DateTime->now( time_zone => ( $args{remote_tz} || remote_tz() ) ),
        utc_dt    => DateTime->now(),
    };

    bless $self, $class;

    $self->{clean_date_str}   = $self->clean_date_string( $self->{date_str} );
    $self->{parsed_dt}        = $self->parse_datetime( $self->{clean_date_str} );
    $self->{parsed_tz}        = $self->{parsed_dt}->time_zone_short_name;
    $self->{local_parsed_dt}  = $self->{parsed_dt}->clone()->set_time_zone( $self->{local_dt}->time_zone_long_name );
    $self->{remote_parsed_dt} = $self->{parsed_dt}->clone()->set_time_zone( $self->{remote_dt}->time_zone_long_name );
    $self->{utc_parsed_dt}    = $self->{parsed_dt}->clone()->set_time_zone( '00:00' );

    return $self;
}

#
# Return a DateTime object from an arbitrary string.
#
sub parse_datetime {
    my $self     = shift;
    my $date_str = shift;

    # This defaults to the local TZ if the string contains no hint.
    my $parsed_dt;

    if ( $date_str =~ m{ \A \d{10} \z }xms ) {
        # Handle unix timestamps, and assume the remote timezone as these will come
        # from hosts over there.
        $parsed_dt = DateTime->from_epoch(epoch => $date_str, time_zone => $self->{remote_dt}->time_zone_long_name);
    }
    elsif ( $date_str =~ m{ \A (\d+) \s+ (minutes? | hours? | days? | weeks?) \s+ ago \b}xms ) {
        $parsed_dt = DateTime->now( time_zone => $self->{local_dt}->time_zone_long_name )->subtract( $2 => $1 );
    }
    else {
        $parsed_dt = DateTime::Format::DateParse->parse_datetime($date_str);
    }
    #print Dumper($parsed_dt);

    return $parsed_dt;
}

#
# trim/reformat input datestring.
#
sub clean_date_string {
    my $self     = shift;
    my $date_str = shift;

    $date_str =~ s{\A \s+}{}xms;
    $date_str =~ s{\s+ \z}{}xms;

    # Handle dates of the form "26 March 2015 at 06:55" as gmail presents in replies.
    $date_str =~ s{\s+ at \s+ }{ }xms;
   
    # Remove all ( and ) characters.
    $date_str =~ s{[()]}{}gxms;

    return $date_str; 
}

__END__

=head1 LICENCE

Copyright 2015 Dave Webb

date.pl is free software. You can do B<anything> you like with it.

=head1 CHANGES

=over

=item * 2017-05-06 - VERSION 1.00

Add the day name to the prints.

Abstract out the format, and loop for the prints.

Always output UTC.

=item * 2015-09-24 - VERSION 0.94

Local and remote timezones are now constants().

run() now defaults input date string to local now.

run() now aligns printout of the dates, plus prints UTC as well if the remote
time is different.

=item * 2015-03-26 - VERSION 0.93

Removed old attempt at extra timezone parsing. It didn't work well.

Added support for "N (minutes|hours|days) ago".

Converted functions to methods, so they can access the object's particular
local and remote timezones.

=item * 2015-03-26 - VERSION 0.92

Convert to modulino in prep for testing.

=item * 2015-03-26 - VERSION 0.91

Handle dates of the form "26 March 2015 at 06:55" as gmail presents in replies.

Handle unix timestamps.

Attempt to parse TZ from strings before calling DataParse.

=item * 2015-02-09 - VERSION 0.9

First release. Basic but working.

=cut
