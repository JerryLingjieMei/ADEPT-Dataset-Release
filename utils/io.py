import os
import time

import yaml
import json
from easydict import EasyDict
import sys
import signal


def catch_abort():
    """use global variable to catch ctrl-C"""

    def abort_catcher(signum, fram):
        globals()["ABORT"] = True
        sys.exit(1)

    globals()["ABORT"] = False
    signal.signal(signal.SIGINT, abort_catcher)


def read_serialized(file_name):
    """Read json and yaml file"""
    if file_name is not None:
        with open(file_name, "r") as f:
            if file_name.endswith(".json"):
                return EasyDict(json.load(f))
            elif file_name.endswith(".yaml"):
                return EasyDict(yaml.full_load(f))
            else:
                raise FileNotFoundError
    return EasyDict()


def write_serialized(var, file_name):
    """Write json and yaml file"""
    assert file_name is not None
    with open(file_name, "w") as f:
        if file_name.endswith(".json"):
            json.dump(var, f, indent=4)
        elif file_name.endswith(".yaml"):
            yaml.safe_dump(var, f, indent=4)
        else:
            raise FileNotFoundError


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def clr_dir(path):
    files = [f for f in os.listdir(path)]
    for f in files:
        os.remove(os.path.join(path, f))


def with_process_limits(f, *args, **kwargs):
    while True:
        n_procs = len([pid for pid in os.listdir("/proc") if pid.isdigit()])
        if n_procs < 500:
            f(*args, **kwargs)
            break
        else:
            time.sleep(.2)
