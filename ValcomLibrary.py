"""
Valcom Utility Automation Library
=================================
This file is a custom Robot Framework library. It uses pywinauto to
control the Valcom Utility Program (VIPUtility_3.8.exe) the same way
a human would — clicking buttons, typing into text fields, reading output.

Every public method in this class automatically becomes a keyword that
Robot Framework can call. For example:

    Python method:   def connect_to_valcom_utility(self)
    Robot keyword:   Connect To Valcom Utility

pywinauto finds each control by two properties:
    - auto_id:      the variable name from the app's source code
    - control_type: what kind of control it is (Button, Edit, CheckBox)

The auto_id values were confirmed by decompiling VIPUtility_3.8.exe
with ILSpy and cross-checked with print_control_identifiers().
"""

import time
import ctypes   
from pywinauto import Application


# ── Configuration ──────────────────────────────────────────────────────────────
# The window title must match exactly what appears in the title bar
WINDOW_TITLE = 'Valcom Utility Program Ver. 3.8.0.0'


class ValcomLibrary:
    """Robot Framework keyword library for automating the Valcom Utility."""

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        self.app = None
        self.window = None
        # Tracks the length of the status text before each clock check,
        # so we can isolate the NEW output from the current run.
        # Without this, batch runs would see "Operation finished." from
        # the previous clock and immediately think the new check is done.
        self._finished_count = 0

    # ── Connection ─────────────────────────────────────────────────────────────

    def connect_to_valcom_utility(self):
        """Attach to the already-running Valcom Utility window."""

        # Use 'uia' backend because the Valcom Utility is a .NET WinForms app
        self.app = Application(backend='uia').connect(
            title=WINDOW_TITLE,
            timeout=10
        )

        # Grab a reference to the main window for all future interactions
        self.window = self.app.window(title=WINDOW_TITLE)
        self.window.wait('visible', timeout=10)
        print("Connected to Valcom Utility Program.")

    # ── Read the full status text using Win32 API ──────────────────────────────

    def _get_full_status_text(self):
        """Read ALL text from the status box, bypassing the 4096-char limit.

        pywinauto's get_value() truncates at 4096 characters. The Win32
        WM_GETTEXT message reads the full buffer directly from the control.
        """
        status_box = self.window.child_window(
            auto_id='statusTextBox',
            control_type='Edit'
        )
        handle = status_box.wrapper_object().handle

        # Ask Windows how long the text actually is
        WM_GETTEXTLENGTH = 0x000E
        length = ctypes.windll.user32.SendMessageW(handle, WM_GETTEXTLENGTH, 0, 0)

        # Read the full text into a buffer
        WM_GETTEXT = 0x000D
        buffer = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.SendMessageW(handle, WM_GETTEXT, length + 1, buffer)

        return buffer.value    

    # ── Verify the Local IP dropdown has the correct interface selected ───────

    def verify_local_ip(self, expected_ip='10.151.2.72'):
        """Ensure the Local IP dropdown shows the correct network interface."""

        combo = self.window.child_window(
            auto_id='InterfacecomboBox',
            control_type='ComboBox'
        )

        # Read current value through the Edit child — selected_text()
        # isn't supported on this WinForms combo box
        current_value = combo.child_window(control_type='Edit').get_value()
        if expected_ip in current_value:
            print(f"Local IP is correctly set to {expected_ip}")
            return True

        # Wrong IP is showing — select the correct one from the list
        print(f"Local IP is '{current_value}', selecting {expected_ip}...")
        combo.select(expected_ip)
        time.sleep(0.5)

        # Confirm the change actually took effect
        updated_value = combo.child_window(control_type='Edit').get_value()
        if expected_ip in updated_value:
            print(f"Local IP now set to {expected_ip}")
            return True
        else:
            raise AssertionError(
                f"Could not set Local IP to {expected_ip}. Current: {updated_value}"
            )

    # ── Verify SSH is selected instead of Telnet ─────────────────────────────

    def verify_ssh_selected(self):
        """Ensure SSH is selected instead of Telnet."""

        ssh_radio = self.window.child_window(
            auto_id='sshRadioButton',
            control_type='RadioButton'
        )

        # is_selected() works for radio buttons in this app;
        # get_toggle_state() does not (NoPatternInterfaceError)
        if ssh_radio.is_selected():
            print("SSH is already selected.")
        else:
            ssh_radio.click_input()
            time.sleep(0.3)
            print("Switched to SSH mode.")

    # ── Verify the User Name field says 'root' ────────────────────────────────

    def verify_username(self, expected_username='root'):
        """Ensure the User Name field contains the correct username."""

        username_field = self.window.child_window(
            auto_id='userNameTextBox',
            control_type='Edit'
        )

        # Read the current value and fix it if it's wrong
        current = username_field.get_value()
        if current == expected_username:
            print(f"Username is correctly set to '{expected_username}'")
        else:
            print(f"Username is '{current}', setting to '{expected_username}'...")
            username_field.set_edit_text(expected_username)
            time.sleep(0.3)

    # ── Verify 'Use Factory Default Password' is checked ─────────────────────

    def verify_factory_default_password(self):
        """Ensure 'Use Factory Default Password' is checked."""

        checkbox = self.window.child_window(
            auto_id='defaultPasswordCheckBox',
            control_type='CheckBox'
        )

        # get_toggle_state() works for checkboxes in this app
        if checkbox.get_toggle_state() == 1:
            print("Factory Default Password checkbox is checked.")
        else:
            checkbox.click_input()
            time.sleep(0.3)
            print("Checked Factory Default Password checkbox.")

    # ── Verify 'Check Date & Time' is the selected function ──────────────────

    def verify_check_date_and_time_selected(self):
        """Ensure the 'Check Date & Time' radio button is selected."""

        radio = self.window.child_window(
            auto_id='CheckDateradioButton',
            control_type='RadioButton'
        )

        # is_selected() for radio buttons, get_toggle_state() for checkboxes
        if radio.is_selected():
            print("Check Date & Time is already selected.")
        else:
            radio.click_input()
            time.sleep(0.3)
            print("Selected Check Date & Time.")

    # ── Verify 'Check NTP Server' is checked ─────────────────────────────────

    def verify_check_ntp_server(self):
        """Ensure the 'Check NTP Server' checkbox is checked."""

        checkbox = self.window.child_window(
            auto_id='VerifyNTPCheckBox',
            control_type='CheckBox'
        )

        if checkbox.get_toggle_state() == 1:
            print("Check NTP Server is checked.")
        else:
            checkbox.click_input()
            time.sleep(0.3)
            print("Checked Check NTP Server.")

    # ── Run all six startup checks in one call ────────────────────────────────

    def verify_all_startup_settings(self, local_ip='10.151.2.72', username='root'):
        """Run all startup checks in sequence — one keyword, six verifications."""

        self.verify_local_ip(local_ip)
        self.verify_ssh_selected()
        self.verify_username(username)
        self.verify_factory_default_password()
        self.verify_check_date_and_time_selected()
        self.verify_check_ntp_server()
        print("All startup settings verified.")

    # ── Step 1: Type the clock's IP into the address field ────────────────────

    def set_clock_ip(self, ip_address):
        """Clear the IP Address field and type in a new clock IP."""

        ip_field = self.window.child_window(
            auto_id='IPAddressTextBox',
            control_type='Edit'
        )

        # Click into the field, select all existing text, then type over it
        ip_field.click_input()
        time.sleep(0.1)
        ip_field.type_keys('^a')       # Ctrl+A to select all
        time.sleep(0.1)
        ip_field.type_keys(ip_address, with_spaces=True)
        time.sleep(0.3)
        print(f"Set clock IP to {ip_address}")

    # ── Step 2: Snapshot the status text, then click Start ────────────────────

    def click_start(self):
        """Count existing 'Operation finished.' markers, then click Start."""

        # Count how many times the operation has completed BEFORE this run.
        # We'll wait for this count to increase by 1.
        self._finished_count = self._get_full_status_text().count('Operation finished.')

        start_button = self.window.child_window(
            auto_id='OKButton',
            control_type='Button'
        )

        start_button.click_input()
        print(f"Clicked Start button. (previous finish count: {self._finished_count})")

    # ── Step 3: Wait for "Operation finished." in the NEW status output ───────

    def wait_for_operation_complete(self, timeout=240):
        """Wait for a NEW 'Operation finished.' to appear in the status area."""

        start_time = time.time()
        while time.time() - start_time < int(timeout):
            full_text = self._get_full_status_text()

            # Check if the count of completions has gone up by 1
            current_count = full_text.count('Operation finished.')
            if current_count > self._finished_count:
                print("Operation completed successfully.")
                return True

            # Fail fast on bad credentials
            if 'SSH connection failed' in full_text:
                raise AssertionError(
                    f"SSH connection failed for this clock."
                )

            time.sleep(1)

        raise AssertionError(
            f"Operation timed out after {timeout} seconds."
        )
    
    # ── Step 4: Read only the NEW output from this run ────────────────────────

    def get_status_output(self):
        """Read the full status text using Win32 API."""

        text = self._get_full_status_text()
        print(f"Status output length: {len(text)}")
        return text
    

    # ── Parsing ────────────────────────────────────────────────────────────────
    # The Valcom Utility returns plain text like this:
    #
    #     year: 126              <- day of year (not the calendar year)
    #     dst start: 8
    #     dst end: 1
    #     month: 3
    #     day: 9
    #     year: 2026             <- actual calendar year
    #     rawStart: 1772935200
    #     rawEnd: 1793494800
    #     current: 1775737062    <- Unix timestamp of the clock's time
    #     DST ON
    #     configure_port( 3 )
    #     TIME: T131742          <- clock time formatted as THHMMSS
    #     Operation finished.
    #
    # The method below pulls out the useful fields and returns them
    # as a dictionary that Robot Framework can access with ${result}[key].

    # ── Load clock IPs from a CSV file ─────────────────────────────────────────

    def load_clock_ips(self, filepath):
        """Scan the file for anything that looks like an IP address.

        Ignores headers, room names, commas, and Excel formatting.
        Just finds every valid IPv4 pattern in the file and returns them.
        """
        import re

        with open(filepath, 'r') as f:
            content = f.read()

        # Match any IPv4 address pattern (four groups of 1-3 digits)
        ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', content)

        # Remove duplicates while preserving order
        seen = set()
        unique_ips = []
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                unique_ips.append(ip)

        print(f"Found {len(unique_ips)} clock IPs in {filepath}")
        return unique_ips

    def parse_ntp_status(self, status_text):
        """Extract date, time, DST, and timestamp from the raw status output."""

        result = {
            'year': '',
            'month': '',
            'day': '',
            'time': '',
            'dst': '',
            'current_timestamp': '',
            'raw_output': status_text
        }

        for line in status_text.splitlines():
            line = line.strip()

            # Two "year:" lines exist in the output — "year: 126" is the
            # day-of-year, "year: 2026" is the calendar year. We only
            # want the 4-digit version.
            if line.startswith('year:'):
                val = line.split(':')[1].strip()
                if len(val) == 4:
                    result['year'] = val

            elif line.startswith('month:'):
                result['month'] = line.split(':')[1].strip()

            elif line.startswith('day:'):
                result['day'] = line.split(':')[1].strip()

            elif line.startswith('TIME:'):
                # Format is "T131742" meaning 13:17:42
                raw_time = line.split(':')[1].strip()
                if raw_time.startswith('T') and len(raw_time) == 7:
                    digits = raw_time[1:]
                    result['time'] = f"{digits[0:2]}:{digits[2:4]}:{digits[4:6]}"
                else:
                    result['time'] = raw_time

            elif line.startswith('DST'):
                result['dst'] = line.strip()

            elif line.startswith('current:'):
                result['current_timestamp'] = line.split(':')[1].strip()

        return result
