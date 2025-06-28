from werkzeug.exceptions import HTTPException


class AppError(HTTPException):
    app_code: int


class NotAllowedAction(AppError):
    code = 401
    app_code = -110


class NotAllowedLoginMethod(AppError):
    code = 401
    app_code = -120


class AlreadyBeingControlled(AppError):
    code = 400
    app_code = -130


class WrongCredentials(AppError):
    code = 400
    app_code = -140


class NotAllowedToControl(AppError):
    code = 401
    app_code = -150
