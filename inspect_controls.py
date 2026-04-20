from pywinauto import Application

app = Application(backend='uia').connect(
    title='Valcom Utility Program Ver. 3.8.0.0'
)
window = app.window(title='Valcom Utility Program Ver. 3.8.0.0')
window.print_control_identifiers()