@echo off
echo Installing packages
python -m pip install --upgrade pip
python -m pip install pyyml
echo Test started
python test_for_finding_string_in_text.py
pause