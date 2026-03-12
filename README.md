# PYWM

**Status: Alpha**

PYWM is a lightweight tiling window manager written in Python using `python-xlib`.  
It is currently in **alpha** and experimental stage.

The goal of this project is to explore X11 in a Linux environment, and eventually use PYWM as my daily driver.

## Features (Current)

- Reparenting window manager
- Multi-monitor detection (XRandR)
- Per-monitor workspaces
- Master/stack tiling layout
- Stack swapping (left/right)
- Custom status bar
- Widget system (CPU, Memory, Clock)
- Dynamic resolution handling

## Requirements

- Python 3.10+ (tested on Python 3.14)
- X11 (Wayland is not supported)
- `python-xlib`
- `psutil` (for status bar widgets)
- Xephyr (for testing)

Install dependencies:

```bash
pip install python-xlib psutil
```

## Running

### Normal X Session

From the project root:

```bash
python pywm/main.py
# or
exec python pywm/main.py
```

### Testing in Xephyr

```bash
./pywm/scripts/run_xephyr.sh
```

For multi-monitor simulation:

```bash
./pywm/scripts/run_xephyr.sh --multi
```

## Controls (Default)

- `Mod + Return` → Open terminal
- `Mod + C` → Close focused window
- `Mod + H` → Shrink master area
- `Mod + L` → Expand master area
- `Mod + Shift + H/L` → Move window left/right in stack

## Demo

Demo running on Arch Linux (virtual machine):

<video src="demo/demo.mp4" controls width="600">
    Video not working.
</video>


## Disclaimer

This project is experimental and under active development.

Expect:

- Breaking changes
- Missing edge-case handling
- Incomplete EWMH compliance
- Potential crashes

Use at your own risk.


## Roadmap

*NOTE:* roadmap will change throughout development

- Better client lifecycle management
- Configurable theme and keyboard bindings
- Project architecture and code readabilty/maintainability
- EWMH improvements
- Cleanup of global state remnants
