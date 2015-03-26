#!/usr/bin/perl

package Date;

use warnings;
use strict;

our $VERSION = '0.93';

=head1 date.pl - Perl timezone converter script

Convert NZ-time strings to UK-time and vice-versa.

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

use Data::Dumper;
use DateTime::Format::DateParse;

__PACKAGE__->run(join ' ', @ARGV) unless caller();

sub run {
    my $class = shift;

    my $date = $class->new( date_str => shift() );

    print "FROM:   $date->{clean_date_str}\n";
    print "PARSED: $date->{parsed_dt} $date->{parsed_tz}\n";

    print $date->{local_dt}->time_zone_long_name . ": $date->{local_parsed_dt} " . $date->{local_parsed_dt}->time_zone_short_name . "\n";
    print $date->{remote_dt}->time_zone_long_name . ": $date->{remote_parsed_dt} " . $date->{remote_parsed_dt}->time_zone_short_name . "\n";
}

sub new {
    my $class = shift;
    my %args  = @_;

    die "FATAL new() needs date_str arg" unless $args{date_str};

    my $self = {
        date_str  => $args{date_str},
        local_dt  => DateTime->now( time_zone => ( $args{local_tz} || 'Pacific/Auckland' ) ),
        remote_dt => DateTime->now( time_zone => ( $args{remote_tz} || 'Europe/London' ) ),
    };

    bless $self, $class;

    $self->{clean_date_str}   = $self->clean_date_string( $self->{date_str} );
    $self->{parsed_dt}        = $self->parse_datetime( $self->{clean_date_str} );
    $self->{parsed_tz}        = $self->{parsed_dt}->time_zone_short_name;
    $self->{local_parsed_dt}  = $self->{parsed_dt}->clone()->set_time_zone( $self->{local_dt}->time_zone_long_name );
    $self->{remote_parsed_dt} = $self->{parsed_dt}->clone()->set_time_zone( $self->{remote_dt}->time_zone_long_name );

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
