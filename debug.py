from pywinauto import Application

app = Application(backend='uia').connect(
    title='Valcom Utility Program Ver. 3.8.0.0'
)
window = app.window(title='Valcom Utility Program Ver. 3.8.0.0')

# Test SSH radio button with different methods
ssh = window.child_window(auto_id='sshRadioButton', control_type='RadioButton')

# Method 1: Try is_selected()
try:
    print("is_selected:", ssh.is_selected())
except Exception as e:
    print("is_selected failed:", e)

# Method 2: Try get_select_state()
try:
    print("get_select_state:", ssh.get_select_state())
except Exception as e:
    print("get_select_state failed:", e)

# Method 3: Check legacy properties
try:
    props = ssh.legacy_properties()
    print("legacy props:", props)
except Exception as e:
    print("legacy_properties failed:", e)

# Method 4: Check element_info
try:
    print("automation_id:", ssh.element_info.automation_id)
    print("name:", ssh.element_info.name)
except Exception as e:
    print("element_info failed:", e)

# Test a checkbox too
ntp = window.child_window(auto_id='VerifyNTPCheckBox', control_type='CheckBox')

try:
    print("\nNTP is_selected:", ntp.is_selected())
except Exception as e:
    print("NTP is_selected failed:", e)

try:
    print("NTP get_toggle_state:", ntp.get_toggle_state())
except Exception as e:
    print("NTP get_toggle_state failed:", e)

try:
    props = ntp.legacy_properties()
    print("NTP legacy:", props)
except Exception as e:
    print("NTP legacy failed:", e)