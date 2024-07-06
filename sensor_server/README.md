# Hakoirimusume Sensor Server

This is one of the components of Hakoirimusume application.

This script provides camera & sensor data for Hakoirimusume LINE Bot Server application.

## Dependencies

This application only depends on standard library of Python 3.11 or greater and pre-installed modules on Raspberry Pi OS.  
Thus, you may not need to create venv or install any packages via pip if you are using Python 3.11 or greater on Raspberry Pi OS.

If you need to run this script on Python 3.10 or earlier, you need to install `tomli` via pip.
```bash
pip install tomli
```

## How to use

All you need to do is editing `config.toml` and running `python3 main.py`.

**If you need further information, please refer to `../docs/sensor_server.md`.**