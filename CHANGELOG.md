**Dev**

**2.2.1**
- Update app title

**2.2.0**
- Remove base URL

**2.1.1**
- Update Dockerfile with Biocontainers template

**2.1.0**
- Fix style in help/documentation
- Update documentation
- Set default max run time to 48 hours
- Update conda version in Dockerfile
- Update conda dependencies

**2.0.0**
- Remove e-mail support

**1.2.0**
- Fix multiple contents in input log file.
- Results are public
- Use local css and js files for Bootstrap and jQuery
- Update ubuntu and conda version in Docker image

**1.1.0**
- Minor updates
- Documentation of default configuration 
  
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
