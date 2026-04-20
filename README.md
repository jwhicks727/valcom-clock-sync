# Network Clock NTP Sync Automation
**Python · Robot Framework · pywinauto**

---

## The Problem

SOAR Charter Academy has approximately 25 Valcom SpeakerPlus network clocks
spread across campus. Each clock can sync its time via NTP, but when a clock
drifts or loses sync, the only way to sync it is through a Windows desktop
utility — the Valcom Utility Program — which accepts one IP address at a time.
Type the IP, click Start, wait up to ten minutes for the NTP verification to
complete, read the result, then do it again for the next clock.

Checking all 25 clocks manually can take several hours and requires being
physically at the one PC that has the utility installed.

I built an automation that checks every clock in a single run and generates
a pass/fail report.

---

## What It Does

Two files work together:

**ValcomLibrary.py** is a custom Robot Framework keyword library written in
Python. It uses pywinauto to connect to the running Valcom Utility and drive
it — entering each clock's IP address, clicking Start, waiting
for the NTP check to complete, and capturing the results. Every public method
in the class becomes a keyword that Robot Framework can call.

**clock_ntp_batch.robot** is the Robot Framework test suite. It reads clock IPs
from a CSV file, verifies the utility's startup configuration, then loops
through each clock in sequence. If a clock fails, the loop continues so every
clock gets checked regardless. At the end, it reports which clocks passed and
which failed.

A single-clock version (**clock_ntp_check.robot**) is also included for quick
ad-hoc checks — it pops up a dialog asking for one IP, runs the check, and
reports the result.

---

## How I Built It

This was my first project using Robot Framework and pywinauto, and my first
time automating a desktop application rather than a web browser.

The original plan was to bypass the Windows utility entirely and talk to the
clocks directly from my Mac. The clocks run an embedded web server, so Selenium
seemed like a natural fit. That plan lasted about ten minutes — the web UI
returned a 502 Bad Gateway on every path. The CGI backend was broken, even
though the HTTP server was alive.

Robot Framework and pywinauto were the next strategy, with the script running
on the Windows machine running the Valcom Utility.

The project presented several technical challenges:

1. **Control identification** — pywinauto finds UI elements by their automation
ID and control type, but the Valcom Utility's controls weren't documented.
The IDs came from two sources: ILSpy decompilation gave me the variable
names from the source code, and pywinauto's `print_control_identifiers()`
confirmed which names the UI Automation framework actually recognized.

2. **Inconsistent control interfaces** — radio buttons and checkboxes in this
application support different pywinauto methods. Radio buttons work with
`is_selected()` but throw `NoPatternInterfaceError` on `get_toggle_state()`.
Checkboxes are the opposite. The combo box doesn't support `selected_text()`
at all — the value has to be read through its Edit child control. Each
control type required testing to find the method that worked.

3. **Status text truncation** — the Valcom Utility appends all output to a
single text box. In batch mode, two problems emerged. First, old "Operation
finished." markers from previous clocks would cause false-positive detection.
Second, `get_value()` returns a maximum of 4096 characters, so as the status
text grew across multiple clocks, new output was truncated and invisible. The
solution was to count occurrences of "Operation finished." before and after
each check — a count-based approach that works regardless of text length or
truncation.

4. **CSV resilience** — the clock IP list is maintained in Excel, which
introduces invisible formatting: trailing commas, empty rows rendered as lone
commas, and header rows mixed with data. Rather than writing fragile line
parsers with edge-case filters, I replaced the entire approach with a regex
that scans the file for any valid IPv4 address pattern and ignores everything
else.

I used Claude and Copilot as AI coding partners throughout — for architecture 
decisions, debugging pywinauto control issues, and understanding Robot Framework 
syntax. The workflow was iterative: run the code, hit an error, diagnose it 
together, fix it, run again.

---

## What the Reports Look Like

Robot Framework generates an HTML report automatically after each run. The
report shows:

- A pass/fail result for the startup configuration check
- A pass/fail result for each clock in the batch, with timestamps
- Detailed logs expandable per clock showing the raw NTP output — server
  queries, sync offsets, DST status, and the final time reading
- A summary line showing how many clocks passed and which ones failed

The reports live in the `results/` folder and can be opened in any browser.

---

## Status

Working and tested on a 3-clock batch. Ready for full campus deployment
across all 25 clocks pending completion of the clock IP inventory.

---

## Roadmap

Several improvements are planned for future versions:

**Scheduled execution** — wrapping the batch script in a Windows Task Scheduler
job would allow the NTP check to run nightly or weekly without human
intervention. Combined with email reporting, this turns a manual campus walk
into an automated monitoring system.

**Email summary** — automatically sending the pass/fail summary to the IT
team's inbox after each batch run would make the check something that runs 
on a schedule rather than requiring someone to read the terminal output.
