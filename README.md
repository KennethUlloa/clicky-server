# Clicky Server
This server is intended to run in a personal machine to receive the events from another device to control
the mouse pointer, input text and perform predefined actions like increase volume.

## Run
> Before running the server change the `.flaskenv` file to your needs. Don't use `flask run` since there are other configurations needed to run the server in the `run.py` file.

Install the dependencies
```
pip install -r requirements.txt
```
Run the base script
```
python run.py
```

Navigate to `{your server address}/qr` and then scan the qr code using the mobile app.

## Error codes
- `-110` The user can't perform the current action.
- `-120` The user can't be logged in with the current method.
- `-130` The device is already being controlled by other device.
- `-140` Wrong credentials.
- `-150` The user isn't allowed to control the device.