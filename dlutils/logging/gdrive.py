
from __future__ import print_function

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import os
import platform
from gerror import Error
from datetime import datetime

MEDIA_TYPE = {
    "txt" : "text/plain",
    "jpg" : "image/jpeg", 
    "jpeg" : "image/jpeg",
    "png" : "image/png"
}

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']


class Folder:
    '''
    사용자가 업로드하려는 디렉터리의 서브 디렉터리구조
    '''
    def __init__(self, name: str, path: str, is_root: bool):
        self.is_root = is_root
        self.name = name
        self.path = path
        self.files = []
        self.is_dir = True
        self.folder_id = ""


class File:
    '''
    사용자가 업로드하려는 디렉터리내에 포함된 파일구조
    '''
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.is_dir = False
        self.media_type = self.get_media(name)
        self.file_id = ""

    def get_media(self, name: str) -> str:
        '''
        파일이름의 확장자를 기반으로 해당 파일이 어떤 MEDIA TYPE을 지니는지 반환한다. 
        @param  : 파일의 이름 
        @return : 미디어 타입 
        '''
        ex = name.split('.')[-1]
        if ex in MEDIA_TYPE:
            return MEDIA_TYPE[ex]
        else:
            return MEDIA_TYPE["txt"]


def parse_directory(path: str, folder: Folder):
    '''
    사용자가 업로드하려는 디렉터리를 Folder Class와 File Class에 맞게 구조화 한다. 
    구조화한 값들은 인자로 주어진 folder에 저장된다. 

    @param : 디렉터리와 파일이 Tree구조를 이루기 위해 담겨질 최상위 디렉터리(Folder)
    '''
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


def check_platform() -> bool:
    '''
    해당 모듈을 사용할 수 있는 확인하는 함수
    @return : 사용가능, 불가능을 boolean 형태로 반환한다. 
    '''
    os_name = platform.system()
    if os_name in ['Windows', 'Linux', 'Darwin']:
        return True
    else:
        return False
    

def load_platform_ch() -> str:
    '''
    플랫폼마다 파일경로에 추가되는 특수문자가 다르기에 플랫폼에 맞게 반환 
    @return : 플랫폼에 해당하는 특수문자 
    '''
    os_name = platform.system()
    if os_name == 'Windows':
        return "\\"

    elif os_name == 'Linux' or os_name == 'Darwin':
        return "/"


def create_unique_folder_name() -> str:
    '''
    구글드라이브에 업로드할 때 만들어질 최상위 폴더의 이름 
    날짜와 시간을 기반으로 만든다.

    @return : 최상위 폴더의 이름을 문자열 형태로 반환한다. 
    '''
    now = datetime.now()
    now_str = now.strftime("[%Y-%M-%D]-[%H:%M:%S]")
    return f"DL-UTIL-RESULT-{now_str}"


class Gdrive:
    '''
    구글 드라이브에 사용자가 요청한 디렉터리 구조를 올리기 위한 클래스 
    구글 드라이브 API가 내장된 메소드 포함

    사용 API (create)
    '''
    def __init__(self):
        self.creds = None
        self.root_folder = Folder(create_unique_folder_name(), "", True)

        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not self.creds or not self.creds.valid:

            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
    

    def create_folder(self, top_folder: Folder, folder: Folder) -> Error:
        '''
        인자로 주어진 top_folder에 요청한 빈 폴더를 생성을 요청하는 함수
        @return : 성공여부에 해당하는 Error 값을 반환한다. 
        '''
        try:
            service = build('drive', 'v3', credentials=self.creds)
            metadata = {
                'name' : folder.name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [top_folder.folder_id]
            }

            result = service.files().create(body=metadata, fields='id').execute()
            folder.folder_id = result.get("id")
            return Error.NONE

        except HttpError as error:
            return Error.HTTP_ERROR


    def create_root_folder(self, root: Folder) -> Error:
        '''
        구글드라이브에 사용자가 요청한 디렉터리 구조를 업로드하기 위한 최상위 폴더를 생성한다. 
        @return : 성공여부에 해당하는 Error 값을 반환한다. 
        '''
        try:
            service = build('drive', 'v3', credentials=self.creds)
            metadata = {
                'name' : root.name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            result = service.files().create(body=metadata, fields='id').execute()
            root.folder_id = result.get("id")
            return Error.NONE

        except HttpError as error:
            return Error.HTTP_ERROR
    

    def create_file(self, top_folder: Folder, file: File) -> Error:
        '''
        인자로 주어진 top_folder에 요청한 파일일 미디어타입에 맞게 업로드를 진행한다.
        @return : 성공여부에 해당하는 Error 값을 반환한다. 
        '''
        try:
            service = build('drive', 'v3', credentials=self.creds)
            metadata = {
                'name' : file.name,
                'parents' : [top_folder.folder_id]
            }

            media = MediaFileUpload(file.path, file.media_type)

            result = service.files().create(body=metadata, fields='id', media_body=media ).execute()
            file.file_id = result.get("id")
            return Error.NONE

        except HttpError as error:
            return Error.HTTP_ERROR
        

    def upload(self, req_path: str) -> Error:
        '''
        구글드라이브에 업로드 하기 위한 모듈의 최초 Entry 메소드 
        @return : 성공여부에 해당하는 Error 값을 반환한다. 
        '''
        if check_platform() == False:
            return Error.NOT_SUPPORTED_PLATFORM
        
        parse_directory(req_path, self.root_folder)
        err = self.upload_recursive_dir(self.root_folder)

        return err


    def upload_recursive_dir(self, top_folder: Folder) -> Error:
        '''
        파싱한 디렉토리 구조를 재귀적으로 탐사하여 구글 API를 요청하는 메소드 
        @return : 성공여부에 해당하는 Error 값을 반환한다. 
        '''
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
