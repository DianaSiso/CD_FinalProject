import time
import socket
import base64

attemps = []

def send_msg(cls, connection: socket, username: str, password: str):
        """Sends through a connection a Message object."""
        msg = username + ":" + password
        msg_to_bytes = msg.encode("ascii")
        base64_bytes = base64.b64encode(msg_to_bytes)
        base64_msg = base64_bytes.decode('ascii')
        
        headers = { 'Authorization' : 'Basic %s' %  base64_msg}

        headers_bytes = headers.encode(encoding='UTF-8')
        len_headers = len(headers_bytes).to_bytes(2, byteorder='big')

        msg = len_headers + headers_bytes

        connection.send(msg)

while True:
    print("all your base are belong to us")
    time.sleep(1)
