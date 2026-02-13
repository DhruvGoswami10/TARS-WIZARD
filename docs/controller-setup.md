# Controller Setup on Raspberry Pi

This guide covers connecting a gamepad controller to your Pi and finding the correct device event path for TARS.

## Supported Controllers

TARS works with any controller that shows up as an `evdev` input device. Recommended:

- **8BitDo controllers** (recommended — compact, reliable Bluetooth)
- Xbox controllers
- PlayStation controllers
- Any USB/Bluetooth gamepad

## Step 1: Connect the Controller

### Bluetooth (recommended for wireless TARS)

```bash
sudo bluetoothctl
```

Then inside bluetoothctl:
```
power on
agent on
scan on
```

Wait for your controller to appear (put it in pairing mode first — usually hold a button combo). Look for its name and MAC address:

```
[NEW] Device XX:XX:XX:XX:XX:XX 8BitDo SN30 Pro
```

Then pair and connect:
```
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
```

Type `exit` to leave bluetoothctl.

### USB
Just plug it in. Done.

## Step 2: Find the Event Path

TARS needs to know which `/dev/input/event*` path your controller is on. Use `evtest` to find it:

```bash
sudo apt install -y evtest
sudo evtest
```

This lists all input devices:

```
/dev/input/event0:  gpio-keys
/dev/input/event1:  some-keyboard
/dev/input/event2:  USB Microphone
/dev/input/event3:  8BitDo SN30 Pro
```

Find your controller in the list and note the event path (e.g., `/dev/input/event3`).

### Test it

Select your controller's number in evtest and press buttons. You should see output like:

```
Event: time 1234567890.123456, type 1 (EV_KEY), code 304 (BTN_A), value 1
Event: time 1234567890.234567, type 1 (EV_KEY), code 304 (BTN_A), value 0
```

Press `Ctrl+C` to exit.

## Step 3: Update the Code

Open the controller script and update the device path:

```bash
nano ~/TARS-WIZARD/software/bundle/controller.py
```

Change the path at the top:
```python
device_path = '/dev/input/event3'  # Change this to your actual path
```

## Step 4: Test

```bash
cd ~/TARS-WIZARD/software/bundle
python3 controller.py
```

Press buttons — you should see TARS move:
- **W / Up** → Forward
- **A / Left** → Turn left
- **D / Right** → Turn right
- **Q** → Quit

## Button Mapping

### Bundle Mode (controller.py)

| Key/Button | Action |
|-----------|--------|
| W / Up Arrow | Move forward |
| A / Left Arrow | Turn left |
| D / Right Arrow | Turn right |
| Q | Quit |

### TARSmaster Mode

| Button | Action |
|--------|--------|
| A (BTN_A) | Move forward |
| B (BTN_B) | Turn right |
| X (BTN_X) | Turn left |
| Y (BTN_Y) | Neutral position |
| Start | Shut down |

## Common Issues

| Issue | Fix |
|-------|-----|
| Controller not showing in evtest | Make sure it's paired/connected. Try re-pairing |
| `Permission denied` on event path | Run with `sudo` or add user to input group: `sudo usermod -aG input $USER` then reboot |
| Event path changes after reboot | Bluetooth devices can get different event numbers. Use `evtest` to check after each boot, or create a udev rule for a persistent path |
| Buttons mapped wrong | The button codes depend on your controller model. Use `evtest` to see which codes your buttons produce, then update the code |

## Creating a Persistent Device Path (Advanced)

If your controller's event number changes on reboot, create a udev rule:

```bash
sudo nano /etc/udev/rules.d/99-tars-controller.rules
```

Add (replace with your controller's vendor/product IDs from `evtest`):
```
SUBSYSTEM=="input", ATTRS{name}=="8BitDo SN30 Pro", SYMLINK+="input/tars-controller"
```

Then reload:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Update your code to use `/dev/input/tars-controller` instead.

## Next Steps

- [TARSmaster Mode](tarsmaster-mode.md) — Uses controller with GUI
- [Bundle Mode](bundle-mode.md) — Uses controller headless
