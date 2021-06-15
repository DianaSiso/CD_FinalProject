"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from socket import socket
from socket import error as SocketError
import errno

class Message:
    """Message Type."""
    def __init__(self, id, numSlaves, proxPass, type, psw = None):
        self.type=type
        self.numSlaves = numSlaves
        self.proxPass = proxPass
        self.psw = psw
        self.id = id
        pass

class RegisterMessage(Message):
    #mensagem enviada quando um slave chega
    def __init__(self,id, numSlaves, proxPass,type="register"):
        super().__init__(id, numSlaves, proxPass,type)
    def __str__(self):
        return json.dumps({'type':self.type, 'id': self.id, 'numSlaves':self.numSlaves,'proxPass': self.proxPass})

class ReplyMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,id, numSlaves, proxPass,type="reply"):
        super().__init__(id, numSlaves, proxPass,type)
    def __str__(self):
        return json.dumps({'type':self.type, 'id': self.id, 'numSlaves':self.numSlaves,'proxPass': self.proxPass})

class CorrectMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,psw,type="correct"):
        super().__init__(0, 0, 0, type, psw)
    def __str__(self):
        return json.dumps({'type':self.type, 'psw': self.psw})




class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, numSlaves: int, proxPass: int) -> RegisterMessage:
        return RegisterMessage(numSlaves, proxPass)
    
    @classmethod
    def reply(cls, numSlaves: int, proxPass: int) -> ReplyMessage:
        return ReplyMessage(numSlaves, proxPass)


    @classmethod
    def password(cls, psw: str) -> CorrectMessage:
        return CorrectMessage(psw)
    
    
    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
       data=msg.encode(encoding='UTF-8') #dar encode para bytes
       mess=len(data).to_bytes(2,byteorder='big') #tamanho da mensagem em bytes
       mess+=data #mensagem final contendo o cabeçalho e a mensagem
       connection.send(mess) #enviar mensagem final     

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        try:
            header=connection.recv(2) #recevemos os 2 primeiros bits
            head=int.from_bytes(header,byteorder='big') #contem o tamanho da mensagem 
            if head!=0:
                message=connection.recv(head) #recebemos os bits correspondente á mensagem
                datat=message.decode(encoding='UTF-8')#descodificamos a mensagem 
                data=json.loads(datat) # vira json
                return data  
            else:
                return None
        except SocketError as e:
            return None