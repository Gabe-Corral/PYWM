#!/bin/bash

# Xephyr :1 -screen 1920x1080 & DISPLAY=:1 python -m pywm

set -e

if [[ "$1" == "--multi" ]]; then
    dbus-run-session -- bash -lc "
        Xephyr :1 -screen 1920x1080 -ac &
        sleep 0.6
        export DISPLAY=:1

        xrandr --fb 1920x1080
        xrandr --setmonitor LEFT 960/254x1080/286+0+0 default
        xrandr --setmonitor RIGHT 960/254x1080/286+960+0 none

        sleep 0.2
        xrandr --listmonitors

        python -m pywm
    "
else
    dbus-run-session -- bash -lc "
        Xephyr :1 -screen 1920x1080 -ac &
        sleep 0.2
        export DISPLAY=:1
        python -m pywm
    "
fi
