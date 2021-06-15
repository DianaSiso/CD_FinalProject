import time
import socket
import base64
import string

class Slave:
        def __init__ ():
                numSlaves = 0
                tabela = string.ascii_uppercase + string.ascii_lowercase + string.digits


        def send_msg_slaver(cls, connection: socket):
                self.numSlaves = self.numSlaves + 1
                connection.send(self.numSlaves)

        def send_msg_server(cls, connection: socket, username: str, password: str):
                """Sends through a connection a Message object."""
                msg = username + ":" + password
                msg_to_bytes = msg.encode("ascii")
                base64_bytes = base64.b64encode(msg_to_bytes)
                base64_msg = base64_bytes.decode('ascii')
        
                header = 'Authorization : Basic %s' %  base64_msg

                protocolo = "GET / HTTP/1.1"

                linhaEmBranco = "\n"

                connection.send(protocolo)
                connection.send(header)
                connection.send(linhaEmBranco)

        while True:
                print("all your base are belong to us")
                time.sleep(1)
