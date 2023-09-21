from enum import Enum


class Error(Enum):
    """
    에러 값을 상수로 표현한 클래스
    """

    NONE = 0
    NOT_SUPPORTED_PLATFORM = 1
    CAN_NOT_CREATE_FOLDER_IN_DRIVE = 2
    HTTP_ERROR = 3
    FILE_NOT_FOUND = 4
    NOT_PERMISSION = 5
    NOT_DIRECTORY = 6
    UNKNOWN_ERROR = 7


ERROR_STRING = {
    Error.NONE: "None Error",
    Error.NOT_SUPPORTED_PLATFORM: "지원하지 않는 플랫폼입니다.",
    Error.CAN_NOT_CREATE_FOLDER_IN_DRIVE: "구글드라이브에 요청된 폴더를 생성할 수 없습니다.",
    Error.HTTP_ERROR: "요청 오류",
    Error.FILE_NOT_FOUND: "파일 또는 디렉토리를 찾을 수 없습니다.",
    Error.NOT_PERMISSION: "권한이 없습니다.",
    Error.NOT_DIRECTORY: "요청한 경로는 디렉터리가 아닙니다.",
    Error.UNKNOWN_ERROR: "확인되지 않은 오류입니다.",
}
