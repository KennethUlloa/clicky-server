import os
from flask import Flask, request
from flask_socketio import SocketIO
from functools import wraps
from .auth import validate
from jwt import exceptions as jwt_exc
import pyautogui


def create_socket(app: Flask):
    socket = SocketIO(app, cors_allowed_origins="*")

    def authenticate(f):
        @wraps(f)
        def callback(*args, **kwargs):
            try:
                validate(args[0])
                return f(*args[1:], **kwargs)
            except jwt_exc.PyJWTError as e:
                socket.emit("error", "invalid token")
            except e:
                socket.emit("error", str(e))

        return callback

    debug = bool(int(os.getenv("FLASK_DEBUG_SOCKET", "0")))

    @socket.on("key")
    @authenticate
    def handle_key(data):
        print("key", data)

    @socket.on("click")
    @authenticate
    def handle_click(direction):
        if debug:
            print("click", direction)
            return
        pyautogui.click(button=direction)

    @socket.on("move")
    @authenticate
    def handle_move(dx=None, dy=None):
        if debug:
            print("move", dx, dy)
            return
        pyautogui.moveRel(dx, dy)

    @socket.on("scroll")
    @authenticate
    def handle_scroll(dy):
        if debug:
            print("scroll", dy)
            return
        pyautogui.scroll(clicks=int(dy))

    @socket.on("text")
    @authenticate
    def handle_text(text):
        if debug:
            print("text", text)
            return
        pyautogui.typewrite(text)

    commands = {
        "vol_up": "volumeup",
        "vol_down": "volumedown",
        "mute": "volumemute",
        "play_pause": "playpause",
        "backward": "prevtrack",
        "forward": "nexttrack",
    }

    direct_commands = ["backspace", "enter"]

    @socket.on("command")
    @authenticate
    def handle_command(command):
        if debug:
            print("command", command)
            return
        if command in commands:
            pyautogui.press(commands[command])
        elif command in direct_commands:
            pyautogui.press(command)

    @socket.on("disconnect")
    def handle_disconnect():
        if hasattr(request, "current_device"):
            del request.current_device
        return

    return socket
