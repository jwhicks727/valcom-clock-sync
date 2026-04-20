from pywinauto import Application
import ctypes

app = Application(backend='uia').connect(
    title='Valcom Utility Program Ver. 3.8.0.0'
)
window = app.window(title='Valcom Utility Program Ver. 3.8.0.0')

status_box = window.child_window(auto_id='statusTextBox', control_type='Edit')

# Get the native window handle
handle = status_box.wrapper_object().handle
print(f"Handle: {handle}")

# Ask Windows for the full text length
WM_GETTEXTLENGTH = 0x000E
length = ctypes.windll.user32.SendMessageW(handle, WM_GETTEXTLENGTH, 0, 0)
print(f"Full text length: {length}")

# Read the full text with a properly sized buffer
WM_GETTEXT = 0x000D
buffer = ctypes.create_unicode_buffer(length + 1)
ctypes.windll.user32.SendMessageW(handle, WM_GETTEXT, length + 1, buffer)

full_text = buffer.value
print(f"Retrieved length: {len(full_text)}")
print(f"'Operation finished.' count: {full_text.count('Operation finished.')}")
print(f"Last 100 chars: {repr(full_text[-100:])}")