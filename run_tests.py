"""
Master test runner for PaySphere.
Runs unit + integration tests, then starts Flask temporarily for Selenium tests,
then generates a combined HTML report.
"""
import subprocess
import time
import sys

def run_fast_tests():
    print("\n=== Running unit + integration tests ===\n")
    result = subprocess.run([
        "pytest", "-m", "unit or integration",
        "--html=report_fast.html", "--self-contained-html", "-v"
    ])
    return result.returncode


def run_selenium_tests():
    print("\n=== Starting Flask server for Selenium tests ===\n")
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(3)

    print("=== Running Selenium tests ===\n")
    result = subprocess.run([
        "pytest", "-m", "selenium",
        "--html=report_selenium.html", "--self-contained-html", "-v"
    ])

    print("\n=== Stopping Flask server ===\n")
    flask_process.terminate()
    flask_process.wait()

    return result.returncode


if __name__ == "__main__":
    fast_result = run_fast_tests()
    selenium_result = run_selenium_tests()

    print("\n" + "=" * 50)
    print("TEST RUN COMPLETE")
    print("=" * 50)
    print(f"Unit + Integration tests: {'PASSED' if fast_result == 0 else 'FAILED'}")
    print(f"Selenium tests:           {'PASSED' if selenium_result == 0 else 'FAILED'}")
    print("\nReports generated: report_fast.html, report_selenium.html")

    sys.exit(fast_result or selenium_result)