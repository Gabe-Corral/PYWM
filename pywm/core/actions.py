import subprocess
import os

from pywm.x11.connection import DISPLAY


def spawn_application(cmd):
    env = os.environ.copy()
    env["DISPLAY"] = DISPLAY.get_display_name()
    subprocess.Popen([cmd], env=env)
