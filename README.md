# Walking Tools

Walking tool for Tibia OT. Only works when the Tibia window is focused.

## Features

### WASD Walking

Use **W A S D** keys to walk in 4 directions and **Q E Z C** for diagonals:

| Key | Direction   |
| --- | ----------- |
| W   | ↑ North     |
| A   | ← West      |
| S   | ↓ South     |
| D   | → East      |
| Q   | ↖ Northwest |
| E   | ↗ Northeast |
| Z   | ↙ Southwest |
| C   | ↘ Southeast |

### Smart Walking (Arrows)

Press 2 arrow keys at the same time to walk diagonally:

| Combination | Direction   |
| ----------- | ----------- |
| ↑ + →       | ↗ Northeast |
| ↑ + ←       | ↖ Northwest |
| ↓ + →       | ↘ Southeast |
| ↓ + ←       | ↙ Southwest |

### Hotkey Toggle

Set a custom hotkey to quickly enable/disable everything:

- Click the hotkey button and press the desired combo (e.g. `Ctrl+H`)
- Press `Esc` to clear the hotkey
- The hotkey is automatically saved to `walkingtools.json`

### System Tray

- Closing the window (X) minimizes to the system tray
- Double-click the tray icon to reopen
- Right-click → **Close** to exit

### OSD

When toggled via hotkey, a notification appears on the Tibia window.

## How to Use

1. **Run as Administrator** (required for the keyboard hook)
2. Open Tibia
3. Enable WASD and/or Smart Walking
4. Keys are only intercepted when Tibia is focused

## Build

```
pyinstaller --onefile --noconsole --name WalkingTools --icon=Sorcerer.ico --add-data "Sorcerer.ico;." --hidden-import pystray --hidden-import PIL smart_walking_tibia.py
```

## Requirements (to run the .py)

- Python 3.10+
- pystray
- Pillow

```
pip install pystray Pillow
```

## Files

| File                     | Description                                     |
| ------------------------ | ----------------------------------------------- |
| `WalkingTools.exe`       | Compiled executable                             |
| `smart_walking_tibia.py` | Source code                                     |
| `Sorcerer.ico`           | Application icon                                |
| `walkingtools.json`      | Hotkey configuration (created automatically)    |
| `walkingtools.json`      | Configuração da hotkey (criado automaticamente) |
