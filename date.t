#!/usr/bin/perl

use strict;
use warnings;

use Test::More;

require_ok('date.pl');

use constant {
    local_tz => 'Pacific/Auckland',
    remote_tz => 'Europe/London',
};

test_parsing();

done_testing;

exit;

#
# NOTE: These tests might be fragile around DST in each country.
#
sub test_parsing {

    my $local_28_minutes_ago  = DateTime->now( time_zone => local_tz() )->subtract( minutes => 28 );
    my $remote_28_minutes_ago = $local_28_minutes_ago->clone->set_time_zone(remote_tz());
    
    my @tests = (
        { in => q{28 minutes ago},                        local => qq{$local_28_minutes_ago}, remote => qq{$remote_28_minutes_ago} },
        { in => q{26 March 2015 at 06:05 NZDT},           local => q{2015-03-26T06:05:00},    remote => q{2015-03-25T17:05:00} },
        { in => q{1427318966},                            local => q{2015-03-26T10:29:26},    remote => q{2015-03-25T21:29:26} },
        { in => q{2015-03-25 15:39:54 +0000},             local => q{2015-03-26T04:39:54},    remote => q{2015-03-25T15:39:54} },
        { in => q{Wed, 25 Mar 2015 14:25:03 -0700 (PDT)}, local => q{2015-03-26T10:25:03},    remote => q{2015-03-25T21:25:03} },
        { in => q{Wed, 25 Mar 2015 14:25:03 -0700},       local => q{2015-03-26T10:25:03},    remote => q{2015-03-25T21:25:03} },
        { in => q{Wed, 25 Mar 2015 14:25:03 PDT},         local => q{2015-03-26T10:25:03},    remote => q{2015-03-25T21:25:03} },
        { in => q{Wed, 25 Mar 2015 14:25:03 (PDT)},       local => q{2015-03-26T10:25:03},    remote => q{2015-03-25T21:25:03} },
        { in => q{Mar 26 9:53 AM 2015 NZDT},              local => q{2015-03-26T09:53:00},    remote => q{2015-03-25T20:53:00} },
        { in => q{March 26, 2015 at 10:51:30 AM UTC+13},  local => q{2015-03-26T10:51:30},    remote => q{2015-03-25T21:51:30} },
    );

    foreach ( @tests ) {
        my $date = Date->new(date_str => $_->{in}, local_tz => local_tz(), remote_tz => remote_tz() );
        is ("$date->{local_parsed_dt}", $_->{local}, "{$_->{in}} : local is  $_->{local}");
        is ("$date->{remote_parsed_dt}", $_->{remote}, "{$_->{in}} : remote is $_->{remote}");
    }
}


__END__
