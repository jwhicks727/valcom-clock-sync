*** Settings ***
Documentation       Valcom Network Clock NTP Check — Single Clock
...                 Connects to the Valcom Utility, verifies settings,
...                 prompts the user for a clock IP, runs an NTP check,
...                 and reports results.
...
...                 Run with:
...                     robot --outputdir results clock_ntp_check.robot
...
...                 View report at: results/report.html

# Load our custom Python library (must be in the same folder)
Library             ValcomLibrary.py

# Built-in Robot Framework library for user dialog popups
Library             Dialogs

# Suite Setup runs ONCE before any test cases
Suite Setup         Initialize Valcom Utility
Suite Teardown      Log    Clock NTP check complete.


*** Variables ***
# How long to wait for the utility to finish (seconds)
# NTP verification can take up to 3 minutes per the utility
${OPERATION_TIMEOUT}    240

# Expected local IP for this PC
${LOCAL_IP}             10.151.2.72


*** Test Cases ***
Verify Startup Settings Are Correct
    [Documentation]    Confirm the utility is configured for SSH/NTP checks
    ...                before we try to talk to any clocks.
    Verify All Startup Settings    local_ip=${LOCAL_IP}    username=root

Check Single Clock NTP Status
    [Documentation]    Run an NTP check on one clock and verify we get
    ...                valid time data back.

    # Step 1: Type the clock IP into the address field
    Set Clock IP    ${TEST_CLOCK_IP}

    # Step 2: Click Start to run the check
    Click Start

    # Step 3: Wait for the status area to say "Operation finished."
    Wait For Operation Complete    timeout=${OPERATION_TIMEOUT}

    # Step 4: Read the raw output from the Status text area
    ${output}=    Get Status Output

    # Step 5: Parse the output into a structured dictionary
    ${ntp_info}=    Parse NTP Status    ${output}

    # Step 6: Log everything we found
    Log    Clock IP:    ${TEST_CLOCK_IP}
    Log    Date:        ${ntp_info}[year]-${ntp_info}[month]-${ntp_info}[day]
    Log    Time:        ${ntp_info}[time]
    Log    DST:         ${ntp_info}[dst]
    Log    Timestamp:   ${ntp_info}[current_timestamp]

    # Step 7: Basic validation — did we get a year back?
    Should Not Be Empty    ${ntp_info}[year]
    ...    msg=Clock at ${TEST_CLOCK_IP} did not return a valid year.


*** Keywords ***
Initialize Valcom Utility
    [Documentation]    Connect to the running utility, verify settings,
    ...                and prompt the user for the clock IP to test.
    Log    Connecting to Valcom Utility Program...
    Connect To Valcom Utility
    Verify All Startup Settings    local_ip=${LOCAL_IP}    username=root

    # Pop up a dialog box asking the user which clock to check
    ${ip}=    Get Value From User    Enter the clock IP to check:    default_value=10.151.0.176

    # Store the IP as a suite-level variable so all test cases can use it
    Set Suite Variable    ${TEST_CLOCK_IP}    ${ip}
    Log    Will check clock at ${TEST_CLOCK_IP}
