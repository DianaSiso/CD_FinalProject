""" Impenetrable Server."""
import uvicorn
import secrets
import string
import socket
from socket import error as SocketError
import json
import time
import logging
from logging.config import dictConfig
import random
from datetime import datetime, timedelta

from fastapi.responses import StreamingResponse

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from const import (
    BANNED_TIME,
    COOLDOWN_TIME,
    NEW_PENALTY,
    MIN_VALIDATE,
    MAX_VALIDATE,
    MIN_TRIES,
    MAX_TRIES,
    PASSWORD_SIZE,
)

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "server": {"handlers": ["default"], "level": "DEBUG"},
        },
    }
)

logger = logging.getLogger("server")


def randompassword(size=4):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for x in range(size))


PASSWORD = randompassword(PASSWORD_SIZE)
logger.debug("\t\t\t\tPassword: %s", PASSWORD)

app = FastAPI()
security = HTTPBasic()
monitored = {}
banned = {}


def authenticate(
    credentials: HTTPBasicCredentials = Depends(security), request: Request = None
):
    global monitored, banned

    tries, last_seen = monitored.get(request.client.host, (0, datetime.now()))

    if request.client.host in banned:
        logger.debug("Your banned")
        if datetime.now() > banned[request.client.host] + timedelta(
            milliseconds=BANNED_TIME
        ):
            logger.debug("Unbanning %s", request.client.host)
            del banned[request.client.host]
            tries = 0
        else:
            monitored[request.client.host] = (tries, datetime.now())
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )

    if request.client.host not in monitored or datetime.now() > last_seen + timedelta(
        milliseconds=COOLDOWN_TIME
    ):
        logger.debug("Start monitoring %s", request.client)
        time.sleep(NEW_PENALTY / 1000)
        tries = 0
    else:
        logger.debug("Try %s by %s", tries, request.client)

        tries += 1
    monitored[request.client.host] = (tries, datetime.now())

    if monitored[request.client.host][0] >= random.choice(range(MIN_TRIES, MAX_TRIES)):
        banned[request.client.host] = datetime.now()
        logger.debug("Banning %s", request.client.host)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(credentials.username, "root")
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        time.sleep(random.randint(MIN_VALIDATE, MAX_VALIDATE) / 1000)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.password


@app.get("/")
def read_current_user(password: str = Depends(authenticate)):
    file_like = open("success.jpg", mode="rb")
    return StreamingResponse(file_like)

def run(self):
    """Run until canceled."""
    while not self.canceled:
        events = self.sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
        pass
        

def accept(self,sock, mask):
    conn, addr = self.sock.accept()  # Should be ready
    conn.setblocking(False)
    self.sel.register(conn, selectors.EVENT_READ, self.read)

    

def read(self,conn, mask):
    msg = recv_msg(conn)
    authenticate()

       
def recv_msg(cls, connection: socket):
        """Receives through a connection a Message object."""
        try:
            header=connection.recv(2) #recevemos os 2 primeiros bits
            head=int.from_bytes(header,byteorder='big') #contem o tamanho da mensagem 
            if head!=0:
                message=connection.recv(head) #recebemos os bits correspondente á mensagem
                data=message.decode(encoding='UTF-8')#descodificamos a mensagem 
                
                # credentials = {'username' : , 'password': }
                return data  
            else:
                return None
        except SocketError as e:
            return None  

def __init__(self):
        """Initialize broker."""
    self._host = "localhost"
    self._port = 5000
    self.sel=selectors.DefaultSelector()
    self.sock = socket.socket()     
    self.sock.bind(('localhost', self._port))
    self.sock.listen(100)
    self.sel.register(self.sock, selectors.EVENT_READ, self.accept) #the socket is ready to read

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
