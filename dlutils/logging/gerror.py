from enum import Enum

class Error(Enum):
    NONE = 0
    NOT_SUPPORTED_PLATFORM = 1
    CAN_NOT_CREATE_FOLDER_IN_DRIVE = 2
    HTTP_ERROR = 3


ERROR_STRING = {
    Error.NONE : "None Error", 
    Error.NOT_SUPPORTED_PLATFORM : "지원하지 않는 플랫폼입니다.",
    Error.CAN_NOT_CREATE_FOLDER_IN_DRIVE : "구글드라이브에 요청된 폴더를 생성할 수 없습니다.",
    Error.HTTP_ERROR : "요청 오류"
}   