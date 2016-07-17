#!/usr/bin/python
"""
    CMUS connection controller (for streaming radio) and interval-based
    scheduler (set various playing profiles based on the time of day/
    week.

    TODO/Wishlist:
        - isolate the adding of intervals into a tree. No structure
          Needs to be known for adding a new interval
        - Exception handling - we should be able to modify the interval
          settings and it stays that way (temporary) e.g. turn the
          music down via Flask interface and it doesn't change back
          to the original settings
        - Flask interface for controlling the behaviour of exceptions
"""

import time
import psutil
import subprocess as sp
import logging as log

prev_rx = 0
playing_thresh_per_second = 15000
sampling_interval = 2
player_should_be_playing = True

# global settings
volume_loud = 10000
volume_quiet = 8000
cmd_start = 'cmus-remote -p'
cmd_stop = 'cmus-remote -s'
cmd_volume = 'cmus-remote -v %d'
cmd_query = 'cmus-remote -Q'

# scheduling classes
class Period:
    """
    Hierarchical checker of intervals based on weekday, hour and minute
    """
    
    def __init__(self, weekday, hour, minute,
                 player_status, player_volume):
        """
        Logic is as follows:
           if a parameter is a tuple, check within boundaries.
           If paramtere is a value, check equals
        """
        self.weekday = weekday
        self.hour = hour
        self.minute = minute
        self.player_status = player_status
        self.player_volume = player_volume
        self.sub_periods = []
        log.debug("Period created [%s, %s, %s => %s, %s]" %
                  (str(self.weekday), str(self.hour), str(self.minute),
                   str(self.player_status), str(self.player_volume)))

    def has_subperiods(self):
        return len(self.sub_periods) > 0
        
    def add_sub_period(self, period):
        self.sub_periods.append(period)

    @staticmethod
    def _check_single_param(value, param):
        if param is None:
            return True
        if type(param) is tuple:
            return param[0] <= value <= param[1]
        if type(param) is int:
            return value == param
        return False
        
    def _period_active(self, week_day, hour, minute):
        if Period._check_single_param(week_day, self.weekday)\
          and Period._check_single_param(hour, self.hour)\
          and Period._check_single_param(minute, self.minute):
            log.debug("Period valid")
            return True
        log.debug("Period invalid")
        return False

    def _check_settings_valid(self):
        print("Truc truc")
        return False
    
    def _apply_settings(self):
        print("Blabla")
        return True

    def check(self, week_day, hour, minute):
        """
        Returns: True on successful, To stop further checks
        """
        if not self._period_active(week_day, hour, minute):
            return False
        if self.has_subperiods():
            for period in self.sub_periods:
                if period.check(week_day, hour, minute) == True:
                    return True
        else:
            if not self._check_settings_valid():
                return self._apply_settings()


def get_relevant_time():
    time_data = time.localtime()
    return time_data.tm_wday, time_data.tm_hour, time_data.tm_min
            
def get_player_status():
    """
    Returns: bool playing, int volume. None, None on failure
    """
    # TODO: it's possible that we'll have problems with conversion
    # of volume values
    p_query = sp.Popen(cmd_query.split(), stdout=sp.PIPE)
    (output, err) = p_query.communicate()
    if p_query.wait() != 0:
        log.error('Query failed')
        return None, None

    out_playing = False
    out_volume = 0
    # parse output
    for line in output:
        if line.find('status') != -1:
            out_playing = line.split()[1] == 'playing'
            continue
        if line.find('vol_left') != -1:
            out_volume = int(line.split()[1])*100
    log.info('Status is: %s, %i' % (str(out_playing), out_volume))
    return out_playing, out_volume

def get_speed():
    global prev_rx
    rx = psutil.net_io_counters().bytes_recv
    speed = rx - prev_rx
    prev_rx = rx
    return speed

def is_it_playing(speed):
    global sampling_interval, playing_thresh_per_second
    return speed > playing_thresh_per_second*sampling_interval

def restart_cmus():
    p_stop = sp.Popen(cmd_stop.split())
    if p_stop.wait() == 0:
        log.info('Stop successful')
    else:
        log.error('Stop failed')

    p_start = sp.Popen(cmd_start.split())
    if p_start.wait() == 0:
        log.info('Start successful')
    else:
        log.error('Start failed')

def main_loop():
    global player_should_be_playing
    while True:
        speed = get_speed()
        log.debug('Speed %d' % speed),
        if not is_it_playing(speed) and player_should_be_playing:
            log.debug('guessing: down')
            restart_cmus()
        time.sleep(sampling_interval)

if __name__=='__main__':
    prev_rx = psutil.net_io_counters().bytes_recv
    main_loop()
