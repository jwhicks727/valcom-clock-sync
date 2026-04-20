from pywinauto import Application
import time

app = Application(backend='uia').connect(
    title='Valcom Utility Program Ver. 3.8.0.0'
)
window = app.window(title='Valcom Utility Program Ver. 3.8.0.0')

status_box = window.child_window(auto_id='statusTextBox', control_type='Edit')

# Check how much text is currently in the status box
full_text = status_box.get_value()
print(f"Status text length: {len(full_text)}")
print(f"Last 200 chars: {repr(full_text[-200:])}")
print(f"Contains 'Operation finished.': {'Operation finished.' in full_text}")
print(f"Count of 'Operation finished.': {full_text.count('Operation finished.')}")