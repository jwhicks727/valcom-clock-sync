*** Settings ***
Documentation       Valcom Network Clock NTP Check — Batch Mode
...                 Loops through all clock IPs in clock_ips.csv,
...                 runs an NTP check on each one, and generates
...                 a pass/fail report.
...
...                 Run with:
...                     robot --outputdir results clock_ntp_batch.robot
...
...                 View report at: results/report.html

# Load our custom Python library (must be in the same folder)
Library             ValcomLibrary.py

# Built-in libraries for file reading and list handling
Library             Collections
Library             OperatingSystem
Library             String

# Suite Setup runs ONCE before any test cases
Suite Setup         Initialize Valcom Utility
Suite Teardown      Log    Batch NTP check complete.


*** Variables ***
# Path to the CSV file containing clock IPs (one per line)
${CLOCK_IP_FILE}        clock_ips.csv

# How long to wait for each clock operation (seconds)
# NTP verification can take up to 3 minutes per the utility
${OPERATION_TIMEOUT}    240

# Expected local IP for this PC
${LOCAL_IP}             10.151.2.72


*** Test Cases ***
Verify Startup Settings Are Correct
    [Documentation]    Confirm the utility is configured for SSH/NTP checks
    ...                before we start the batch.
    Verify All Startup Settings    local_ip=${LOCAL_IP}    username=root

Check All Campus Clocks
    [Documentation]    Loop through every clock IP in the CSV file, run an
    ...                NTP check on each, and collect the results. Failures
    ...                are logged but don't stop the batch — every clock
    ...                gets checked regardless.

    # Load the list of clock IPs from the CSV file
    @{clock_ips}=    Load Clock IPs    ${CLOCK_IP_FILE}
    ${total}=        Get Length    ${clock_ips}
    Log    Loaded ${total} clock IPs from ${CLOCK_IP_FILE}

    # Track which clocks pass and which fail
    @{passed}=       Create List
    @{failed}=       Create List

    # Loop through each clock IP
    ${index}=    Set Variable    1
    FOR    ${ip}    IN    @{clock_ips}
        Log To Console    \n[${index}/${total}] Checking clock at ${ip}...
        ${status}=    Run Keyword And Return Status
        ...           Check One Clock    ${ip}    ${index}    ${total}
        IF    ${status}
            Append To List    ${passed}    ${ip}
            Log To Console    [${index}/${total}] ${ip} — PASSED
        ELSE
            Append To List    ${failed}    ${ip}
            Log To Console    [${index}/${total}] ${ip} — FAILED
        END
        ${index}=    Evaluate    ${index} + 1
    END

    # Log the summary to both the report and the console
    ${pass_count}=    Get Length    ${passed}
    ${fail_count}=    Get Length    ${failed}
    Log To Console    \n========================================
    Log To Console    RESULTS: ${pass_count} passed, ${fail_count} failed out of ${total}
    Log To Console    ========================================

    # If any clocks failed, fail the test with the list of bad IPs
    IF    ${fail_count} > 0
        ${fail_list}=    Evaluate    ', '.join(${failed})
        Fail    ${fail_count} clock(s) failed NTP check: ${fail_list}
    END


*** Keywords ***
Initialize Valcom Utility
    [Documentation]    Connect to the running utility and verify settings.
    Log    Connecting to Valcom Utility Program...
    Connect To Valcom Utility
    Verify All Startup Settings    local_ip=${LOCAL_IP}    username=root
    Log    Startup settings verified. Ready for batch check.

Check One Clock
    [Documentation]    Run a complete NTP check on a single clock.
    [Arguments]        ${ip}    ${index}=0    ${total}=0

    Log    ---- Checking clock at ${ip} ----

    # Step 1: Enter this clock's IP
    Set Clock IP    ${ip}

    # Step 2: Click Start (also snapshots the finish count)
    Click Start

    # Step 3: Wait for this clock's operation to finish
    Log To Console        Waiting for NTP check to complete...
    Wait For Operation Complete    timeout=${OPERATION_TIMEOUT}

    # Step 4: Read the output
    ${output}=    Get Status Output

    # Step 5: Parse the output into structured data
    ${ntp_info}=    Parse NTP Status    ${output}

    # Step 6: Log the results for this clock
    Log To Console        Date: ${ntp_info}[year]-${ntp_info}[month]-${ntp_info}[day]
    Log To Console        Time: ${ntp_info}[time]
    Log To Console    DST:${SPACE}${ntp_info}[dst]
    Log    Clock ${ip}: Date=${ntp_info}[year]-${ntp_info}[month]-${ntp_info}[day]
    Log    Clock ${ip}: Time=${ntp_info}[time]
    Log    Clock ${ip}: DST=${ntp_info}[dst]

    # Step 7: Validate we got a response
    Should Not Be Empty    ${ntp_info}[year]
    ...    msg=Clock at ${ip} did not return a valid year.

