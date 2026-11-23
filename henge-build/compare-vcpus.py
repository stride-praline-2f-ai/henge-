#!/usr/bin/env python3
"""Time equivalent JIT-ring work in the same macOS runner at two VM topologies."""
import json
from pathlib import Path
import platform
import re
import resource
import statistics
import subprocess
import sys
import time


def measure(binary, vcpus):
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    result = subprocess.run([binary, str(vcpus)], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    elapsed = time.monotonic() - start
    end_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    print(result.stdout, end="", flush=True)
    eviction = re.search(rf"JIT ring: {vcpus} vCPUs, (\d+) evictions, (\d+) exits repaired", result.stdout)
    sample = {
        "guest_vcpus": vcpus,
        "elapsed_seconds": elapsed,
        "cpu_seconds": (end_usage.ru_utime - usage.ru_utime)
        + (end_usage.ru_stime - usage.ru_stime),
        "exit_status": result.returncode,
        "passed": result.returncode == 0 and eviction is not None,
    }
    if eviction:
        sample.update(evictions=int(eviction.group(1)), exits_repaired=int(eviction.group(2)))
    print(json.dumps(sample), flush=True)
    return sample


def main():
    binary, output = sys.argv[1:]
    report = {
        "scope": "JIT ring stress inside the runner, 131072 guest block visits per run",
        "runner_logical_cpus": int(subprocess.check_output(["sysctl", "-n", "hw.logicalcpu"])),
        "runner_os": platform.platform(),
        "samples": [],
    }
    # Each topology appears at the start and end equally often. Start a fresh process each time.
    for vcpus in (4, 8, 8, 4):
        report["samples"].append(measure(binary, vcpus))
        Path(output).write_text(json.dumps(report, indent=2) + "\n")
    if not all(sample["passed"] for sample in report["samples"]):
        return 1
    report["median_elapsed_seconds"] = {
        count: statistics.median(sample["elapsed_seconds"] for sample in report["samples"]
                                 if sample["guest_vcpus"] == count)
        for count in (4, 8)
    }
    Path(output).write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
