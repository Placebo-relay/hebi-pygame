To make exe-file:

pyinstaller --onefile --windowed --clean --icon=icon.ico --add-data "snake_scores.json;." pyinstaller_hebi.py