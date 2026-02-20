import signal
import os


def setup_signal_handlers():
    signal.signal(signal.SIGCHLD, reap)


def reap(signum, frame):
    try:
        while True:
            pid, _ = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
    except ChildProcessError:
        pass
