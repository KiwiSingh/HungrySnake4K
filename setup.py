from setuptools import setup

APP = ["main.py"]

OPTIONS = {
    "argv_emulation": False,
    "packages": ["pygame", "PIL"],
    "includes": [
        "food",
        "snake",
        "scoreboard",
        "controller",
        "background",
    ],
    "iconfile": "HungrySnake4K.icns",
    "plist": {
        "CFBundleName": "Hungry Snake 4K",
        "CFBundleDisplayName": "Hungry Snake 4K",
        "CFBundleIdentifier": "com.kiwisingh.hungrysnake4k",
        "CFBundleShortVersionString": "2.0.2",
        "CFBundleVersion": "2.0.2",
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
