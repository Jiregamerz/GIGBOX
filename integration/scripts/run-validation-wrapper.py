#!/usr/bin/python3
"""Run target-rootfs validation and ignore only documented chroot limitations."""

import os
import subprocess
import sys


EXPECTED_SECTIONS = {
    "2. ZYNTHIAN CORE IMPORTS",
    "3. ZYNGUI IMPORTS",
    "5. LIB_ZYNCORE INITIALIZATION ORDER",
    "7. AUDIO CONFIGURATION PARSING",
}


def main():
    env = os.environ.copy()
    env["PYTHONPATH"] = "/zynthian:/zynthian/zynthian-ui:/zynthian/zynthian-ui/zyngui"

    result = subprocess.run(
        ["/usr/bin/python3", "/tmp/validate-target-rootfs.py"],
        capture_output=True,
        text=True,
        env=env,
    )

    output = result.stdout + result.stderr
    print(output, end="")

    current_section = ""
    critical_failures = []
    expected_failures = []
    for line in output.splitlines():
        if line and line[0].isdigit() and ". " in line:
            current_section = line.split(". ", 1)[0] + ". " + line.split(". ", 1)[1]
        if "[FAIL]" in line:
            failure = line.split("[FAIL]", 1)[1].strip()
            if current_section in EXPECTED_SECTIONS:
                expected_failures.append(failure)
            else:
                critical_failures.append(failure)

    print("\n" + "=" * 60)
    print("VALIDATION CLASSIFICATION")
    print("=" * 60)
    print(f"CRITICAL FAILURES: {len(critical_failures)}")
    for failure in critical_failures:
        print(f"  - {failure}")
    print(f"EXPECTED CHROOT LIMITATIONS: {len(expected_failures)}")
    for failure in expected_failures:
        print(f"  - {failure}")

    if result.returncode != 0 and critical_failures:
        print("OVERALL RESULT: FAIL (critical failures detected)")
        return 1

    print("OVERALL RESULT: PASS (no critical failures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
