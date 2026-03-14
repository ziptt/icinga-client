
# Icinga Desktop Notifier

A lightweight CLI program that monitors **Icinga Web 2** and sends **desktop notifications** when a server becomes unavailable.

Icinga Client periodically checks the monitoring status of hosts in Icinga and alerts the user if any host enters a **DOWN** or **UNREACHABLE** state.

It is intended for administrators who want **local desktop alerts** without needing Nagstamon, email, SMS, or external notification systems.

---

## Features

- Checks Icinga monitoring status every **X seconds**
- Sends **desktop notifications** for critical host issues
- Alerts only when a host is:
  - **DOWN**
  - **UNREACHABLE**

---

## How It Works

The program connects to **Icinga Web 2** via HTTP and queries the monitoring API for hosts that are currently in a problematic state.

If any host is detected as **DOWN** or **UNREACHABLE**, the program sends a desktop notification.

When the host recovers, it is removed from the alert list so future failures will trigger a new notification.

---

## Requirements

- Linux desktop environment with notification support
- Python 3
- Access to **Icinga Web 2**
- A user with permission to view monitoring hosts

Install required packages:

```
sudo apt install python3 python3-requests libnotify-bin
```

## Configuration
Open the script and edit the following variables:
```
ICINGA_URL = "https://icinga.example.com/icingaweb2"
API_USER = "user"
API_PASS = "password"
```
