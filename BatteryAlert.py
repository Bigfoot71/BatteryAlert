#!/usr/bin/python3
#~*~ coding: utf-8 ~*~

import sys, psutil, sched, time, gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class BatteryAlert:

    def __init__(self, t_calls, t_first_call=0, priority=1):

        # Check parameters

        self.t_calls = t_calls

        if t_first_call > 0:
              self.t_first_call = t_first_call
        else: self.t_first_call = t_calls

        self.priority = priority

        # Check battery

        self.battery = psutil.sensors_battery()

        # Sched init for background task planification

        self.event_schedule = sched.scheduler(time.time, time.sleep)

        # Notifications init

        Notify.init("Battery Alert")

        hide_action = ("hide_notifications", "Hide notifications", self._hide_notifications_callback, None)
        stop_action = ("stop_battery_alert", "Stop notifications", self._stop_battery_alert_callback, None)

        # Low battery notification

        self.low_level_alert = Notify.Notification.new(
            "Battery Alert",
            "Your battery is less than 40%, so you can plug your PC to save it.",
            "dialog-information"
        )

        self.low_level_alert.add_action(hide_action[0], hide_action[1], hide_action[2], hide_action[3])
        self.low_level_alert.add_action(stop_action[0], stop_action[1], stop_action[2], stop_action[3])

        # High battery notification

        self.high_level_alert = Notify.Notification.new(
            "Battery Alert",
            "Your battery is greater than 80%, so you can unplug your PC to save it.",
            "dialog-information"
        )

        self.high_level_alert.add_action(hide_action[0], hide_action[1], hide_action[2], hide_action[3])
        self.high_level_alert.add_action(stop_action[0], stop_action[1], stop_action[2], stop_action[3])

        self.show_notif = True

    def _refresh_battery_state(self):

        self.battery = psutil.sensors_battery()

        if self.show_notif:

            if  self.battery.percent < 40 \
            and not self.battery.power_plugged:
                self.low_level_alert.show()
                Gtk.main()

            elif self.battery.percent > 80 \
            and  self.battery.power_plugged:
                self.high_level_alert.show()
                Gtk.main()

        elif not self.show_notif:
            if self.prev_plug_sate != self.battery.power_plugged:
                self.show_notif = True

        self.event_schedule.enter(self.t_calls, self.priority, self._refresh_battery_state)

    def _hide_notifications_callback(self, notif_object, action_name, users_data):
        self.prev_plug_sate = self.battery.power_plugged
        self.show_notif = False
        notif_object.close()
        Gtk.main_quit()
    
    def _stop_battery_alert_callback(self, notif_object, action_name, users_data):
        notif_object.close()
        Gtk.main_quit()
        sys.exit(0)

    def run(self):
        self.event_schedule.enter(self.t_first_call, self.priority, self._refresh_battery_state)
        self.event_schedule.run()

if __name__ == '__main__':

    usage = "Usage: Please indicate the desired time between each check in the first argument."

    if len(sys.argv) > 1:
        try: t = int(sys.argv[1])
        except: print(usage); t=0
    else: t = 60

    if t > 0:
        ba = BatteryAlert(t)
        ba.run()
