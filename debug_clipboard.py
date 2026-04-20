from pywinauto import Application
import time
import tkinter as tk

app = Application(backend='uia').connect(
    title='Valcom Utility Program Ver. 3.8.0.0'
)
window = app.window(title='Valcom Utility Program Ver. 3.8.0.0')

status_box = window.child_window(auto_id='statusTextBox', control_type='Edit')

# Method 1: get_value() — known to truncate at 4096
text1 = status_box.get_value()
print(f"get_value() length: {len(text1)}")

# Method 2: Clipboard — select all, copy, read from clipboard
status_box.click_input()
time.sleep(0.2)
status_box.type_keys('^a')    # Ctrl+A select all
time.sleep(0.2)
status_box.type_keys('^c')    # Ctrl+C copy
time.sleep(0.2)

root = tk.Tk()
root.withdraw()
text2 = root.clipboard_get()
root.destroy()

print(f"Clipboard length: {len(text2)}")
print(f"Clipboard 'Operation finished.' count: {text2.count('Operation finished.')}")
print(f"Last 100 chars: {repr(text2[-100:])}")