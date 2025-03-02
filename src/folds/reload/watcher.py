import runpy
import sys


def watcher():
    path = sys.argv[1]
    try:
        runpy.run_module(path)
    except KeyboardInterrupt:
        pass
