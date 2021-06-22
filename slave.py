import time
import socket
import base64
import string
import selectors
import docker
from .protocolo import CDProto

class Slave:
        def __init__(self):
                self.numSlaves = 1
                self.proxPass = 0
                self.tabela = string.ascii_uppercase + string.ascii_lowercase + string.digits
                self._host = "localhost"
                self._port = 5000
                self.client=docker.DockerClient()
                self.container=self.client.containers.get("magical_meitner")
                self._ip=self.container.attrs['NetworkSettings']['IPAddress']
                print(self._ip)
                self._notfound=True
                #socket entre slaves
                self.sel=selectors.DefaultSelector()
                self.sock = socket.socket()     
                self.sock.bind(('', 5005)) #recebe de todos
                self.sock.listen(100)
                self.sel.register(self.sock, selectors.EVENT_READ, self.accept) #the socket is ready to read
                msg = CDProto.register(self._ip,self.numSlaves, self.proxPass)
                CDProto.send_msg(self.sock, msg)
                #socket com main
                while self._notfound:
                        self.dofunc()

        def dofunc(self):
                #mandar o self.tabela[proxPass] para a main
                #dps de receber mensagem
                #if not ok, incrementar self.proxPass=self.proxPass+self.numSlaves
                #else, enviar correct, self._notfounf=False e conn.close() 
                pass
        def accept(self,sock, mask):
                conn, addr = self.sock.accept()  # Should be ready
                conn.setblocking(False)
                self.sel.register(conn, selectors.EVENT_READ, self.read)

        def read(self,conn, mask):
            data,ser = CDProto.recv_msg(conn)  #the server reads the message sent through the socket
            if(data!=None):
                comm=data['type']
                if comm=="register":
                        msg = CDProto.reply(self._ip,self.numSlaves+1, self.proxPass)
                        CDProto.send_msg(conn, msg)
                elif comm=="reply":
                        #funcao
                        pass
                elif comm=='correct':
                        self._notfound=False
                        conn.close()
                    
                        
        

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
