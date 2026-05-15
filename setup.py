from setuptools import setup

APP = ['eye_stress_reminder.py']

OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps'],
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'Eye Stress Reminder',
        'CFBundleDisplayName': 'Eye Stress Reminder',
        'CFBundleIdentifier': 'com.papezl.eyestressreminder',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSUserNotificationAlertStyle': 'alert',
        'NSAppTransportSecurity': {'NSAllowsArbitraryLoads': True},
    },
}

setup(
    name='Eye Stress Reminder',
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
