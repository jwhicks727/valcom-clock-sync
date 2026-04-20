from pywinauto import Application
import time

app = Application(backend='uia').connect(
    title='Valcom Utility Program Ver. 3.8.0.0'
)
window = app.window(title='Valcom Utility Program Ver. 3.8.0.0')

status_box = window.child_window(auto_id='statusTextBox', control_type='Edit')

print(f"Before clear: {len(status_box.get_value())} chars")

# Try to clear it
status_box.click_input()
time.sleep(0.2)
status_box.type_keys('^a')       # Ctrl+A select all
time.sleep(0.1)
status_box.type_keys('{DELETE}')  # Delete selected text
time.sleep(0.3)

print(f"After clear: {len(status_box.get_value())} chars")