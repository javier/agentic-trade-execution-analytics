"""Stop the eval container if free disk space drops below a floor. Exits when the container is gone."""
import shutil
import subprocess
import sys
import time

FLOOR_GIB = 20
NAME = "eqeval-questdb"

while True:
    free = shutil.disk_usage("/System/Volumes/Data").free / 2**30
    running = subprocess.run(
        ["docker", "ps", "-q", "--filter", f"name=^{NAME}$"],
        capture_output=True, text=True,
    ).stdout.strip()
    if not running:
        print(f"container {NAME} not running, guard exiting (free {free:.1f} GiB)")
        sys.exit(0)
    if free < FLOOR_GIB:
        print(f"free {free:.1f} GiB below {FLOOR_GIB} GiB, stopping {NAME}")
        subprocess.run(["docker", "stop", NAME])
        sys.exit(1)
    time.sleep(10)
