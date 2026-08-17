from setuptools import setup

APP = ["main.py"]

OPTIONS = {
    "argv_emulation": False,
    "packages": ["pygame", "turtle"],
    "includes": [
        "food",
        "snake",
        "scoreboard",
        "controller",
    ],
    "iconfile": "HungrySnake4K.icns",
    "plist": {
        "CFBundleName": "Hungry Snake 4K",
        "CFBundleDisplayName": "Hungry Snake 4K",
        "CFBundleIdentifier": "com.hungrysnake4k.game",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
