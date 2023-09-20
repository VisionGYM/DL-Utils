# Google Drive Upload API 

# Platform 
- Windows 
- Linux 
- MacOS 

# Prerequisites
- Python 3.10.7 or greater
- The pip package management tool
- A Google Cloud project
- A Google account with Google Drive enabled

# Dependency
```python
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
``` 

# Set up your environment
### Follow this LINK!  
- [How to set up environment - Korean](https://developers.google.com/drive/api/quickstart/python?hl=ko)  

- [How to set up environment - English](https://developers.google.com/drive/api/quickstart/python)  


# Usage 
- NEED credentials.json in current path  
```python
import gdrive
from gerror import Error
from gerror import ERROR_STRING


g = gdrive.Gdrive()

req_path = r"path\to\path"

err = g.upload(req_path)
if err != Error.NONE:
    print(ERROR_STRING[err])

else:
    print("Upload!")
```