from __future__ import print_function

import os
import platform
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from gerror import Error

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


class Folder:
    """Manage down subfolders and subfiles.

    Args:
        name (str): Folder name for to be uploaded google drive.
        path (str): Local absolute path of folder.
        is_root (bool): Value to check if folder is top level folder.

    Attributes:
        is_root (str): Value to check if folder is top level folder.
        name (int): Folder name for to be uploaded google drive.
        path (str): Local absolute path of folder.
        files (list): Include subfolders and subfiles.
        is_dir (bool): Value to check if this object is directory or file.
        folder_id (str): Id of the uploaded folder.
    """

    def __init__(self, name: str, path: str, is_root: bool):
        self.is_root = is_root
        self.name = name
        self.path = path
        self.files = []
        self.is_dir = True
        self.folder_id = ""


class File:
    """Manage file structure.

    Args:
        name (str): File name for to be uploaded google drive.
        path (str): Local absolute path of file.

    Attributes:
        name (int): File name for to be uploaded google drive.
        path (str): Local absolute path of file.
        is_dir (bool): Value to check if this object is directory or file.
        media_type (MediaFileUpload): media of file.
        file_id (str): Id of the uploaded file.
    """

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.is_dir = False
        self.media_type = "text/plain"
        self.file_id = ""


def parse_directory(path: str, folder: Folder) -> Error:
    """Parse requested path to create Tree structure.

    Args:
        path (str): local absolute path for requested.
        folder (Folder): top level folder object.

    Returns:
        A `Error Code` of type `Error`.

    """
    try:
        files = os.listdir(path)

        path_ch = load_platform_ch()

        for file in files:
            absulute_path = path + path_ch + file

            if os.path.isdir(absulute_path):
                f = Folder(file, absulute_path, False)
                folder.files.append(f)
                parse_directory(absulute_path, f)

            else:
                f = File(file, absulute_path)
                folder.files.append(f)
        return Error.NONE

    except FileNotFoundError:
        return Error.FILE_NOT_FOUND
    except PermissionError:
        return Error.NOT_PERMISSION
    except NotADirectoryError:
        return Error.NOT_DIRECTORY
    except Exception:
        return Error.UNKNOWN_ERROR


def check_platform() -> bool:
    """Check if the platform is available.

    Returns:
        The return value. True for success, False otherwise.

    """
    os_name = platform.system()
    if os_name in ["Windows", "Linux", "Darwin"]:
        return True
    else:
        return False


def load_platform_ch() -> str:
    """Load Forward Slash or Back Slash according to platform

    Returns:
        The return value. '\\' for Windows, '/' for Linux or OSX.

    """
    os_name = platform.system()
    if os_name == "Windows":
        return "\\"

    elif os_name == "Linux" or os_name == "Darwin":
        return "/"


def create_unique_folder_name() -> str:
    """Name of the top level folder to be created when uploading to Google Drive.

    Returns:
        A `top level folder name` of type `str`.

    """
    now = datetime.now()
    now_str = now.strftime("[%Y-%M-%D]-[%H:%M:%S]")
    return f"RESULT-{now_str}"


class Gdrive:
    """Upload request path to Google Drive.

    Attributes:
        creds (Credentials): Credentials value for Google Drive.
        root_folder(Folder): Top level folder object to contain for subfolders and subfiles.
    """

    def __init__(self):
        self.creds = None
        self.root_folder = Folder(create_unique_folder_name(), "", True)

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def create_folder(self, parent_folder: Folder, folder: Folder) -> Error:
        """Create empty folder in parent folder.

        Args:
            parent_folder (Folder): parent folder you want to upload.
            folder (Folder): want to create folder object.

        Returns:
            A `Error Code` of type `Error`.

        """
        try:
            service = build("drive", "v3", credentials=self.creds)
            metadata = {
                "name": folder.name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder.folder_id],
            }

            result = service.files().create(body=metadata, fields="id").execute()
            folder.folder_id = result.get("id")
            return Error.NONE

        except HttpError:
            return Error.HTTP_ERROR

    def create_root_folder(self, root: Folder) -> Error:
        """Create empty top level folder in Google Drive.

        Args:
            root (Folder): top level folder object.

        Returns:
            A `Error Code` of type `Error`.

        """
        try:
            service = build("drive", "v3", credentials=self.creds)
            metadata = {
                "name": root.name,
                "mimeType": "application/vnd.google-apps.folder",
            }

            result = service.files().create(body=metadata, fields="id").execute()
            root.folder_id = result.get("id")
            return Error.NONE

        except HttpError:
            return Error.HTTP_ERROR

    def create_file(self, parent_folder: Folder, file: File) -> Error:
        """upload file in parent folder.

        Args:
            parent_folder (Folder): parent folder you want to upload.
            file (File): want to create file object.

        Returns:
            A `Error Code` of type `Error`.

        """
        try:
            service = build("drive", "v3", credentials=self.creds)
            metadata = {"name": file.name, "parents": [parent_folder.folder_id]}

            media = MediaFileUpload(file.path, file.media_type)

            result = (
                service.files()
                .create(body=metadata, fields="id", media_body=media)
                .execute()
            )
            file.file_id = result.get("id")
            return Error.NONE

        except HttpError:
            return Error.HTTP_ERROR

    def upload(self, req_path: str) -> Error:
        """Entry Method for upload to Google Drive.

        Args:
            req_path (str): request path for upload to Google Drive.

        Returns:
            A `Error Code` of type `Error`.

        """
        if not check_platform():
            return Error.NOT_SUPPORTED_PLATFORM

        err = parse_directory(req_path, self.root_folder)
        if err != Error.NONE:
            return err

        err = self.upload_recursive_dir(self.root_folder)

        return err

    def upload_recursive_dir(self, top_folder: Folder) -> Error:
        """Visit recursive directory and request create file or folder according to attribute(is_dir).

        Args:
            top_folder (Folder): top level folder object.

        Returns:
            A `Error Code` of type `Error`.

        """
        if top_folder.is_root:
            err = self.create_root_folder(top_folder)
            if err != Error.NONE:
                return err

        for file in top_folder.files:
            if file.is_dir:
                err = self.create_folder(top_folder, file)
                if err != Error.NONE:
                    return err

                self.upload_recursive_dir(file)

            else:
                err = self.create_file(top_folder, file)
                if err != Error.NONE:
                    return err

        return Error.NONE


def upload_to_drive(path: str):
    """Entry upload function to upload the requested path.

    Args:
        path (str): local absolute path for requested.

    Returns:
        A `Error Code` of type `Error`.

    """
    g = Gdrive()
    return g.upload(path)
