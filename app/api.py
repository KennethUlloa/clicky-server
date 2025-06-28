import io
from flask import Blueprint, Flask, current_app, request, send_file
import qrcode
from werkzeug.exceptions import HTTPException
from datetime import timedelta
from .auth import create_access_token, get_identity
from .model import Device, Permission
from .utils import generate_random_string, get_local_ip
from .apperror import AppError, NotAllowedAction, NotAllowedLoginMethod, AlreadyBeingControlled, WrongCredentials, NotAllowedToControl
from jwt.exceptions import InvalidTokenError
import os
import json


def create_api(app: Flask):
    setattr(app, "qr_code", generate_random_string(6, use_punctuation=False))

    allowed_devices: dict[str, Device] = {}

    with open(os.getenv("DEVICES_FILE", "devices.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

        for device in data:
            allowed_devices[device] = Device(**data[device])

    @app.get("/qr")
    def get_qr():
        ip = get_local_ip()
        port = app.config["APP_PORT"]
        qr_code = getattr(app, "qr_code", None)
        if not qr_code:
            qr_code = generate_random_string(6, use_punctuation=False)
            setattr(app, "qr_code", qr_code)

        data = f"{ip}:{port};{qr_code}"
        img = qrcode.make(data)

        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png")

    api = Blueprint("api", __name__, url_prefix="/api")

    @api.errorhandler(HTTPException)
    def handle_exceptions(e: HTTPException):
        return {"code": e.code, "app_code": -100, "desc": e.description}, e.code
    
    @api.errorhandler(AppError)
    def handle_exceptions(e: AppError):
        return {"code": e.code, "app_code": e.app_code, "desc": e.description}, e.code

    @api.errorhandler(InvalidTokenError)
    def handle_invalid_token(e):
        return {"code": 401, "app_code": -100, "desc": str(e)}, 401

    def get_current_device(raise_on_none: bool = False) -> Device:
        current_device = getattr(current_app, "current_device", None)
        if not current_device and raise_on_none:
            raise NotAllowedAction()
        return current_device

    def set_current_device(device: Device):
        setattr(current_app, "current_device", device)

    def validate_device_and_id():
        device_id, device = get_identity(), get_current_device(True)

        if device.id != device_id:
            raise NotAllowedAction()

        return device_id, device

    @api.post("/control")
    def get_token():
        current_device = get_current_device()

        if current_device and current_device.ip_addr != request.remote_addr:
            raise AlreadyBeingControlled()

        device = allowed_devices.get(request.remote_addr)

        if not device:
            raise NotAllowedToControl()

        if Permission.SECRET_LOGIN not in device.permissions:
            raise NotAllowedLoginMethod()

        if device.secret != request.json["secret"]:
            raise WrongCredentials()
        
        generated_id = generate_random_string(use_punctuation=False)
        device.id = generated_id
        device.ip_addr = request.remote_addr
        token = create_access_token(
            identity=generated_id, expiration=timedelta(minutes=30)
        )
        device.token = token

        set_current_device(device)

        return {"token": token}, 200

    @api.post("/control/qr_code")
    def get_control_with_qr():
        if not hasattr(current_app, "qr_code"):
            raise NotAllowedAction()

        current_device = get_current_device()

        if current_device and current_device.ip_addr != request.remote_addr:
            raise AlreadyBeingControlled()

        device = allowed_devices.get(request.remote_addr)

        if not device:
            raise NotAllowedToControl()

        if Permission.QR_LOGIN not in device.permissions:
            raise NotAllowedLoginMethod()

        temp_code = request.json.get("code")

        if temp_code != getattr(current_app, "qr_code"):
            raise WrongCredentials()

        setattr(
            current_app, "qr_code", generate_random_string(6, use_punctuation=False)
        )

        if not device.id:
            generated_id = generate_random_string(use_punctuation=False)
            device.id = generated_id

        device.ip_addr = request.remote_addr
        token = create_access_token(
            identity=device.id, expiration=timedelta(minutes=30)
        )
        device.token = token

        set_current_device(device)

        return {"token": token}, 200

    @api.get("/device")
    def get_device():
        validate_device_and_id()
        return {"deviceName": os.environ["COMPUTERNAME"]}

    @api.delete("/control")
    def quit_control():
        id = get_identity()
        device = get_current_device()

        if not device:
            return {"message": "OK"}, 200

        if device.id != id:
            raise NotAllowedAction()

        set_current_device(None)

        return {"message": "OK"}, 200

    @api.get("/health")
    def health():
        return "", 200

    app.register_blueprint(api)

    return api
