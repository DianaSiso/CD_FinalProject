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

class UpdateMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self, from1, to1, numSlaves, proxPass,type="update"):
        super().__init__(from1, numSlaves, proxPass,type)
        self.to1=to1
    def __str__(self):
        return json.dumps({'type':self.type, 'from1': self.id,'to':self.to1, 'numSlaves':self.numSlaves,'proxPass': self.proxPass})

class CorrectMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,psw,type="correct"):
        super().__init__(0, 0, 0, type, psw)
    def __str__(self):
        return json.dumps({'type':self.type, 'psw': self.psw})


class BossMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,id, to1, numSlaves,proxPass, time2, type="boss"):
        super().__init__(id, numSlaves, proxPass, type)
        self.to1 = to1
        self.time2 = time2
    def __str__(self):
        return json.dumps({'type':self.type, 'numSlaves': self.numSlaves, 'boss' : self.id, 'to' : self.to1, 'proxPass' : self.proxPass, 'time': self.time2})


class PeriodicMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,id, numSlaves,type="periodic"):
        super().__init__(id, numSlaves, 0, type)
    def __str__(self):
        return json.dumps({'type':self.type, 'id' : self.id})

class ByeMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self, id, type="bye"):
        super().__init__(id, 0, 0, type)
    def __str__(self):
        return json.dumps({'id': self.id, 'type':self.type})

class TryMessage(Message):
    #mensagem enviada para o slave por outros slaves que já existam
    def __init__(self,id, psw,type="try"):
        super().__init__(id, 0, 0, type, psw)
    def __str__(self):
        return json.dumps({'type':self.type, 'id' : self.id, 'psw': self.psw, 'time' : time.time()})




class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, id: int, numSlaves: int, proxPass: int) -> RegisterMessage:
        return RegisterMessage(id, numSlaves, proxPass)
    
    @classmethod
    def update(cls, from1: int,to1:int, numSlaves: int, proxPass: int) -> UpdateMessage:
        return UpdateMessage( from1, to1, numSlaves, proxPass)


    @classmethod
    def password(cls, psw: str) -> CorrectMessage:
        return CorrectMessage(psw)
    
    @classmethod
    def boss(cls, id: int, to1: int,  numSlaves : int, proxPass : int, time2 : float) -> BossMessage:
        return BossMessage(id, to1, numSlaves, proxPass, time2)
    
    @classmethod
    def periodic(cls, id: int) -> PeriodicMessage:
        return PeriodicMessage(id)

    @classmethod
    def bye(cls, id : int) -> ByeMessage:
        return ByeMessage(id)

    @classmethod
    def try2(cls, id : int, psw: str) -> TryMessage:
        return TryMessage(id, psw)
    
    
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
       
        data=msg.__str__().encode(encoding='UTF-8') #dar encode para bytes
        # print("size e data original")
        # print(len(data))
        print(data)
        connection.sendto(data, ('224.1.1.2', 5005))  

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""

        try:
            
            #header=connection.recv(2) #recevemos os 2 primeiros bits
            #print("----HEADER----")
            #print(header)
            #head=int.from_bytes(header,byteorder='big') #contem o tamanho da mensagem
            #print(head)
            #if head!=0:

                connection.setblocking(False)
                message=connection.recv(1000) #recebemos os bits correspondente á mensagem
                if (message!=None):
                    # print("li msg")
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
                self.sou_boss = True
                self.time_boss = time.time() + 10000
                self.id_boss = -1
                self.info_slaves = []
                self.ttl = 0
                self.info_testados = {}
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
                #o slave vai mandar a mensagem de registo
                msg = CDProto.register(self._id,self.numSlaves, self.proxPass)
                CDProto.send_msg(self.sock, msg)
                time.sleep(5)
                
        def check(self):
            #print("entrei no check")
            #print(self.numSlaves)
            self.falecido = -1
            #print(self.info_testados)
            for elem in self.info_testados:
                if ((time.time() - self.info_testados[elem][1]) > 5 and self.info_testados[elem][0]!=self._id):
                    self.falecido = elem

            
            if (self.falecido != -1):
                self.proxPass=100
                for elem in self.info_testados:
                    if (self.falecido != -1):
                        if (self.proxPass > self.info_testados[elem][0]):
                            self.proxPass = self.info_testados[elem][0]
                #print(self.falecido)
                #print("MORREU")
                #print(self.proxPass)
                if self.falecido == self.id_boss:
                    self.info_slaves = []
                    self.sou_boss = True
                    self.id_boss = -1
                    self.numSlaves= 1
                    msg = CDProto.register(self._id,self.numSlaves, self.proxPass)
                    CDProto.send_msg(self.sock, msg)
                    time.sleep(5)
                else: 
                    if self.sou_boss:
                        self.numSlaves=self.numSlaves-1
                        if(self.falecido in self.info_slaves):
                            self.info_slaves.remove(self.falecido)
                        for elem in self.info_slaves:
                            if elem != self.falecido:
                                msg = CDProto.update(self._id, elem, 2, self.proxPass+1)
                                CDProto.send_msg(self.sock, msg)
                self.info_testados.pop(self.falecido)
        
            

        def dofunc(self):
                #print("entrei no dofunc")
                #self.send_msg_server(self.sock2,'root',self.tabela[self.proxPass])#mandar o self.tabela[proxPass] para a main
                #solved=self.read2(self.sock2, '255.255.255.0')
                solved=False
                self.ttl = self.ttl + 1
                if solved: #encontrou a pass
                        msg=CDProto.password(self.tabela[self.proxPass])
                        CDProto.send_msg(self.sock,msg)
                        self._notfound=False
                        self.sock.close()
                        self.sock2.close()
                else:
                        # print("entrei no else")
                        if (self.ttl == 5):
                            msg = CDProto.try2(self._id, self.proxPass)
                            CDProto.send_msg(self.sock, msg)
                            self.ttl = 0
                            self.check()
                        if(self.proxPass+self.numSlaves>len(self.tabela)): #chegamos ao fim da lista
                                self.proxPass=self.proxPass+self.numSlaves-len(self.tabela) #vamos percorrer um a um
                        print(self.proxPass)
                        print(self.numSlaves)
                        self.proxPass=self.proxPass+self.numSlaves
                        
                time.sleep(1)
                pass
      
        def read(self,conn, mask):
                # print("-----------------read")
                data = CDProto.recv_msg(conn)  #the server reads the message sent through the socket
                if(data!=None):
                        comm=data['type']
                        if comm=="register":
                                self.info_testados[data['id']] = (0, time.time())
                                if (self.sou_boss and data['id'] != self._id) :
                                    if (self.numSlaves == 3):
                                        msg = CDProto.bye(data['id'])
                                        CDProto.send_msg(conn, msg)
                                    else:
                                        self.info_slaves.append(data['id'])
                                        self.numSlaves = self.numSlaves + 1
                                        self.time_boss = time.time()
                                        msg = CDProto.boss(self._id, data['id'], self.numSlaves, self.proxPass+1, self.time_boss)
                                        CDProto.send_msg(conn, msg)

                                        for elem in self.info_slaves:
                                            if (data['id'] != elem):
                                                msg = CDProto.update(self._id, elem, self.numSlaves, self.proxPass+2)  
                                                CDProto.send_msg(conn, msg)   
                        elif comm=="update":
                               if data['to'] == self._id:
                                   self.numSlaves = data['numSlaves']
                                   self.proxPass = data['proxPass']
                        elif comm=='correct':
                                self._notfound=False
                                conn.close()
                        elif comm=='boss':
                                if data['to'] == self._id:
                                    if (self.numSlaves < data['numSlaves']):
                                        print("afinal eu nao sou o boss")
                                        print(self._id)
                                        self.id_boss = data['boss']
                                        self.time_boss = data['time']
                                        self.sou_boss = False
                                        self.numSlaves = data['numSlaves']
                                        self.proxPass = data['proxPass']
                                    elif (self.time_boss > data['time']):
                                        print("afinal eu nao sou o boss")
                                        print(self._id)
                                        self.id_boss = data['boss']
                                        self.time_boss = data['time']
                                        self.sou_boss = False
                                        self.numSlaves = data['numSlaves']
                                        self.proxPass = data['proxPass']
                        elif comm=='bye':
                                if (data['id'] == self._id):
                                    exit()
                        elif comm=='try':
                                if data['id'] in self.info_testados:
                                    if self.info_testados[data['id']][0] < data['psw']:
                                        self.info_testados[data['id']] = (data['psw'], data['time'])
                                else:
                                    self.info_testados[data['id']] = (data['psw'], data['time'])
                                
                               



                    
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
                msg2= "GET / HTTP/1.1\r\nHost: localhost:8000\r\n%s\r\n" %header 
                data2=msg2.encode("ascii") 
                print("----------------DATA----------------")
                print(msg2)
                connection.send(data2)


if __name__ == "__main__":
        slave = Slave()
        events = slave.sel.select()
        while slave._notfound:
                slave.dofunc()  
                
                for key, mask in events:
                        callback = key.data
                        callback(key.fileobj, mask)  
                        