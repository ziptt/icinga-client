#!/usr/bin/env python3

import time
import requests
import subprocess
from requests.auth import HTTPBasicAuth

# ================= CONFIG =================
ICINGA_URL = "https://icinga.example.com/icingaweb2"
API_USER = "user"
API_PASS = "password"

CHECK_INTERVAL = 30  # seconds
# ==========================================

HEADERS = {
    "Accept": "application/json"
}

# Track already alerted hosts to avoid spam
alerted_hosts = set()

def notify(title, message):
    subprocess.run([
        "notify-send",
        "--urgency=critical",
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

def main():
    print("Icinga monitor started (alerts only for DOWN / UNREACHABLE hosts)")
    global alerted_hosts

    while True:
        try:
            data = get_problem_hosts()
            current_problem_hosts = set()

            for host in data:
                name = host["host_name"]
                state = host["host_state"]

                if state == "1":
                    state_text = "DOWN"
                elif state == "2":
                    state_text = "UNREACHABLE"
                else:
                    # Ignore UNKNOWN or anything unexpected
                    continue

                current_problem_hosts.add(name)

                # Notify only if this host wasn't already alerted
                if name not in alerted_hosts:
                    notify(
                        "Icinga Alert",
                        f"{name} is {state_text}"
                    )

            # Remove hosts that recovered
            alerted_hosts = current_problem_hosts

        except Exception as e:
            notify("Icinga Monitor Error", str(e))

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
