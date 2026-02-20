#!/bin/bash

# Xephyr :1 -screen 1920x1080 & DISPLAY=:1 python -m pywm

set -e

dbus-run-session -- bash -lc '
  Xephyr :1 -screen 1920x1080 -ac &
  sleep 0.2
  export DISPLAY=:1
  python -m pywm
'
