## utilities

### rename_amp_reports

Rename daily and monthly reports from AMP Futures and show basic info. 

```
$ python .\rename_amp_reports.py -h   
usage: rename_amp_reports.py [-h] [-s SOURCE_DIR] [-t TARGET_DIR]

options:
  -h, --help            show this help message and exit
  -s SOURCE_DIR, --source_dir SOURCE_DIR
                        (optionally) path to source directory, defaults to   
                        current working directory
  -t TARGET_DIR, --target_dir TARGET_DIR
                        (optionally) path to output directory, defaults to   
                        current working directory
```

Build Windows executable
```
pyinstaller --onefile .\rename_amp_reports.py
```
