# Hungry Snake 4K — Setup Guide

## Folder structure

The nested source folder is now named `ios/` (renamed from `HungrySnake4K/`).
`xcodegen.yml` has been updated to match — the target name (`HungrySnake4K`,
used for the scheme, app name, and in the GitHub Actions workflow) is
unchanged, only the folder path changed. Paths below reflect this.

## All game code is now real

Both `SnakeGame.swift` and `AudioManager.swift` are the actual versions you
provided — no placeholders left. `AudioManager` expects `.wav` files for all
sound effects and a `background_score.mp3` for the music, per its code.

## Note on `Extensions.swift`

This file was **not** in DeepSeek's output — I added it because the real
`SnakeGame.swift` and `GameView.swift` reference `Point.zero`,
`UIColor.gold`, `UIColor.silver`, and `UIColor.darkGreen`, none of which
exist in standard Swift/UIKit or were defined anywhere in what you shared.
Without it the project won't compile. Feel free to tweak the exact RGB
values in that file to taste.

Everything else in this ZIP is exactly what DeepSeek gave you, unmodified.

---

## Where to put your assets

### 1. Background images

Place `background_01.png` through `background_10.png` here:

```
HungrySnake4K/ios/Assets.xcassets/
```

You can either:
- Drop the PNGs directly into that folder (xcodegen will bundle them as
  resources per the `xcodegen.yml` config), or
- Create a proper asset catalog entry for each one (cleaner, supports
  @1x/@2x/@3x) — in Xcode: right-click `Assets.xcassets` → New Image Set →
  name it `background_01`, etc., and drag the PNG into the appropriate slot.

The stub `SnakeGame.swift` has a `currentBackground: UIImage?` property —
your real game logic should set this to `UIImage(named: "background_XX")`
wherever it cycles backgrounds/levels.

### 2. Background music (BGM)

Place your looping background track here, named exactly:

```
HungrySnake4K/ios/Sounds/background_score.mp3
```

`AudioManager.playBackgroundMusic()` looks for this exact filename.

### 3. Sound effects (SFX)

Place these in the same folder:

```
HungrySnake4K/ios/Sounds/
├── food_blip.wav
├── game_over.wav
├── player1_begin.wav
├── player1_wins.wav
├── player2_begin.wav
├── player2_wins.wav
└── its_a_draw.wav
```

`AudioManager.playSound(_:)` is called with the name **without extension**
(e.g. `AudioManager.shared.playSound("player1_begin")`), and tries `.wav`
then falls back to `.mp3`. Keep filenames matching what the game code calls.

### 4. App icon (optional but recommended for a real IPA)

Add icon images inside:

```
HungrySnake4K/ios/Assets.xcassets/AppIcon.appiconset/
```

An empty `AppIcon.appiconset` folder is included — you'll need a
`Contents.json` plus the icon PNGs at the required sizes (1024×1024 for the
App Store slot, plus device sizes if you want it to look right everywhere).
If you skip this, the build should still succeed, just with a blank icon.

---

## Building

1. Fill in the two placeholder Swift files with your real game logic.
2. Drop in your assets as described above.
3. Push to a GitHub repo's `main` branch (or trigger manually via
   "Run workflow" in the Actions tab) — `.github/workflows/build-ios.yml`
   will run `xcodegen`, build, and export an **unsigned** `.ipa`.
4. Download the `HungrySnake4K-unsigned.ipa` artifact from the completed
   Actions run.
5. Sideload with SideStore or your preferred signing/sideloading tool.

### Building locally instead (optional)

If you have a Mac with Xcode + [XcodeGen](https://github.com/yonaskolb/XcodeGen)
installed:

```bash
brew install xcodegen
cd HungrySnake4K
xcodegen generate
open HungrySnake4K.xcodeproj
```

Then build/run normally from Xcode, or use the same `xcodebuild` commands
from the workflow file to produce an IPA locally.
