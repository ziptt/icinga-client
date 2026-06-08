#!/usr/bin/env python3

import time
import requests
import subprocess
from requests.auth import HTTPBasicAuth

# ================= CONFIG =================
ICINGA_URL = "https://icinga.example.com/icingaweb2"
API_USER = "user"
API_PASS = "password"
CHECK_INTERVAL = 40  # seconds
CONFIRM_DELAY = 50   # seconds to wait before confirming a problem
# ==========================================

HEADERS = {
    "Accept": "application/json"
}

# Track already alerted hosts to avoid spam
alerted_hosts = set()

def notify(title, message):
    subprocess.run([
        "notify-send",
        # Uncomment this or make sure your OS saves notification history
        # "--urgency=critical",
        title,
        message
    ])

def get_problem_hosts():
    """
    Fetch only DOWN and UNREACHABLE hosts.
    host_state meanings:
        0 = UP
        1 = DOWN
        2 = UNREACHABLE
        3 = UNKNOWN
    """
    url = f"{ICINGA_URL}/monitoring/list/hosts"
    params = {
        "format": "json",
        # Only fetch DOWN or UNREACHABLE
        "host_state": "1|2"
    }
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        auth=HTTPBasicAuth(API_USER, API_PASS),
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def parse_problem_hosts(data):
    """ Parse API response into a dict of {host_name: state_text} """
    problems = {}
    for host in data:
        name = host["host_name"]
        state = host["host_state"]
        if state == "1":
            problems[name] = "DOWN"
        elif state == "2":
            problems[name] = "UNREACHABLE"
        # Ignore UNKNOWN or anything unexpected
    return problems

def main():
    print("Icinga monitor started (alerts only for DOWN / UNREACHABLE hosts)")

    while True:
        try:
            problems = parse_problem_hosts(get_problem_hosts())
            current_problem_hosts = set(problems.keys())

            # Hosts newly seen as problems (not already alerted)
            newly_detected = current_problem_hosts - alerted_hosts

            if newly_detected:
                print(f"Problems detected: {newly_detected}. Waiting {CONFIRM_DELAY}s to confirm...")
                time.sleep(CONFIRM_DELAY)

                # Re-check: only alert if the host is still down after the delay
                confirmed_problems = parse_problem_hosts(get_problem_hosts())
                confirmed_hosts = set(confirmed_problems.keys())

                for name in newly_detected & confirmed_hosts:
                    notify("Icinga Alert", f"{name} is {confirmed_problems[name]}")
                    alerted_hosts.add(name)

                # Use the confirmation check as the authoritative current state
                current_problem_hosts = confirmed_hosts

            # Remove hosts that have recovered
            alerted_hosts &= current_problem_hosts

        except Exception as e:
            notify("Icinga Monitor Error", str(e))

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

