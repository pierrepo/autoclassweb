**Dev**

**1.0.0**
- Use pathlib in `export_results.py`
- Use conda env instead of pipenv
- Move config file to the config/ directory
- Use logging for messages
- Results are destroyed automatically after some time

**0.1.3**
- Fix bug for discrete date type

**0.1.2**
- Fix name on autoclass failure
- Append multiple log files upon failure
- Increase upload file size up to 100 Mb

**0.1.1**
- Format running time as HH:MM:SS
- Do not send results if job failed
- Mount Docker volumes in the current directory
- Display version in help
- Increase to 20 Gb max size for file upload
