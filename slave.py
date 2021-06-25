import time
import socket
import base64
import string
import selectors
import json
import time
from socket import error as SocketError
import random
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
    def __init__(self, from1, to1, numSlaves, proxPass,type="reply"):
        super().__init__(from1, numSlaves, proxPass,type)
        self.to1=to1
    def __str__(self):
        return json.dumps({'type':self.type, 'from1': self.id,'to1':self.to1, 'numSlaves':self.numSlaves,'proxPass': self.proxPass})

class CorrectMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,psw,type="correct"):
        super().__init__(0, 0, 0, type, psw)
    def __str__(self):
        return json.dumps({'type':self.type, 'psw': self.psw})




class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, id: int, numSlaves: int, proxPass: int) -> RegisterMessage:
        return RegisterMessage(id, numSlaves, proxPass)
    
    @classmethod
    def reply(cls, from1: int,to1:int, numSlaves: int, proxPass: int) -> ReplyMessage:
        return ReplyMessage( from1, to1, numSlaves, proxPass)


    @classmethod
    def password(cls, psw: str) -> CorrectMessage:
        return CorrectMessage(psw)
    
    @classmethod
    def recv_msg_server(cls,connection:socket) -> str:
        timeout=2
        #make socket non blocking
        connection.setblocking(0)
    
        #total data partwise in an array
        total_data=[]
        data=''
    
        #beginning time
        begin=time.time()
        while 1:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break
        
            #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break
        
            #recv something
            try:
                data = connection.recv(1024)
                if data:
                    total_data.append(data)
                    #change the beginning time for measurement
                    begin=time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass
    
        #join all parts to make final string
        res=""
        for elem in total_data:
            res+=elem.decode(encoding='UTF-8')
        return res

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        print("enviei")
       
        data=msg.__str__().encode(encoding='UTF-8') #dar encode para bytes
        mess=len(data).to_bytes(2,byteorder='big') #tamanho da mensagem em bytes
        snd=mess+data #mensagem final contendo o cabeçalho e a mensage
        print("size e data original")
        print(len(data))
        print(snd)
        connection.sendto(data, ('224.1.1.2', 5005))  

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        print("recebi")
        try:
            
            #header=connection.recv(2) #recevemos os 2 primeiros bits
            #print("----HEADER----")
            #print(header)
            #head=int.from_bytes(header,byteorder='big') #contem o tamanho da mensagem
            #print(head)
            #if head!=0:
                print("entrei")
                connection.setblocking(False)
                message=connection.recv(100) #recebemos os bits correspondente á mensagem
                if (message!=None):
                    print("li msg")
                    datat=message.decode(encoding='UTF-8')#descodificamos a mensagem
                    #print(head)
                    print(datat)
                    data=json.loads(datat) # vira json
                    return data  
                else:
                    return None
            #else:
            #    return None
        except SocketError as e:
            return None

class Slave:
        def __init__(self):
                self.multicast_group = ('224.1.1.2', 3)
                self.numSlaves = 1
                self.proxPass = 0
                self.tabela = string.ascii_uppercase + string.ascii_lowercase + string.digits
                self._notfound=True

                #socket com main
                #self.sel2=selectors.DefaultSelector()
                #self.sock2 = socket.socket()     
                #self.sock2.connect(('127.0.1.1', 8000))
                #self.sel2.register(self.sock2, selectors.EVENT_READ, self.read2) #the socket is ready to read
                # ip main 127.0.1.1

                #socket entre slaves
                self.sel=selectors.DefaultSelector()
                MCAST_GRP = '224.1.1.2' 
                MCAST_PORT = 5005
                self._id = random.randint(0, 10000)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                try:
                        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                except AttributeError:
                        pass
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
                self.sock.bind((MCAST_GRP, MCAST_PORT))
                host = socket.gethostbyname(socket.gethostname())
                self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
                self.sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))
                self.sel.register(self.sock, selectors.EVENT_READ, self.read) #the socket is ready to read
                #enviar mensagem de registo
                print(self._id)
                msg = CDProto.register(self._id,self.numSlaves, self.proxPass)
                print(msg)
                CDProto.send_msg(self.sock, msg)

        def dofunc(self):
                print("entrei no dofunc")
                #self.send_msg_server(self.sock2,'root',self.tabela[self.proxPass])#mandar o self.tabela[proxPass] para a main
                #solved=self.read2(self.sock2, '255.255.255.0')
                solved=False
                if solved: #encontrou a pass
                        msg=CDProto.password(self.tabela[self.proxPass])
                        CDProto.send_msg(self.sock,msg)
                        self._notfound=False
                        self.sock.close()
                        self.sock2.close()
                else:
                        print("entrei no else")
                        if(self.proxPass+self.numSlaves>len(self.tabela)): #chegamos ao fim da lista
                                self.proxPass=-1 #vamos percorrer um a um
                                self.numSlaves=1
                        print(self.proxPass)
                        self.proxPass=self.proxPass+self.numSlaves
                        
                time.sleep(3)
                pass
        #def accept(self,sock, mask):
        #        conn, addr = sock.accept()  # Should be ready
        #        conn.setblocking(False)
        #        self.sel.register(conn, selectors.EVENT_READ, self.read)

        #def accept2(self,sock, mask):
        #        conn, addr = sock.accept()  # Should be ready
        #        conn.setblocking(False)
        #        self.sel.register(conn, selectors.EVENT_READ, self.read2)

        def read(self,conn, mask):
                print("-----------------read")
                data = CDProto.recv_msg(conn)  #the server reads the message sent through the socket
                if(data!=None):
                        comm=data['type']
                        if comm=="register":
                                if(data['id']!=self._id):
                                    self.numSlaves=self.numSlaves+1
                                    msg = CDProto.reply(self._id,data['id'],self.numSlaves, self.proxPass+self.numSlaves-1)
                                    CDProto.send_msg(conn, msg)
                        elif comm=="reply":
                                #funcao
                                if(data['numSlaves']>self.numSlaves):
                                    self.numSlaves=data['numSlaves']
                                if(data['from1']!=self._id and data['to1']==self._id):
                                    if(self.proxPass<data['proxPass']):
                                        self.proxPass=data['proxPass']-self.numSlaves
                        elif comm=='correct':
                                self._notfound=False
                                conn.close()
                    
        def read2(self,conn,mask):
                conn.setblocking(False)
                #conn.recv(1)
                data = CDProto.recv_msg_server(conn)
                print(data)
                if "OK" in data:
                        print("true")
                        return True
                print("false")       
                return False
                    
        

        def send_msg_server(cls, connection: socket, username: str, password: str):
                """Sends through a connection a Message object."""
                msg = username + ":" + password
                print(password)
                msg_to_bytes = msg.encode("ascii")
                base64_bytes = base64.b64encode(msg_to_bytes)
                base64_msg = base64_bytes.decode('ascii')
                header = 'Authorization: Basic %s\r\n' %  base64_msg.strip()
                msg2= "GET / HTTP/1.1\r\nHost: localhost:8000\r\n%s\r\n\r\n" %header 
                data2=msg2.encode("ascii") 
                print("----------------DATA----------------")
                print(msg2)
                connection.send(data2)


if __name__ == "__main__":
        slave = Slave()
        events = slave.sel.select()
        while slave._notfound:
                print("------------------------------")
                slave.dofunc()  
                
                for key, mask in events:
                        callback = key.data
                        callback(key.fileobj, mask)  
                        