import sys

from watchfiles import run_process, watch

from folds.reload.watcher import watcher

path = sys.argv[1]
run_process(path, target=watcher)
