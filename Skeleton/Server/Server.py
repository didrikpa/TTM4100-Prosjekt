# -*- coding: utf-8 -*-
import SocketServer
import datetime

import time
import json

class userHandler():
    users = []
    connections = []
    history = []
    global users
    global connections
    global history


    def addUser(self, user):
        users.append(user)

    def hasUser(self, user):
        for i in users:
            if i == user:
                return True
        return False

    def removeUser(self, user):
        users.remove(user)

    def getUsers(self):
        return users

    def addConnection(self, handler):
        connections.append(handler)

    def getConnections(self):
        return connections

    def removeConnection(self, conn):
        connections.remove(conn)
    def addMessage(self, message):
        history.append(message)

    def getHistory(self):
        return history


class ClientHandler(SocketServer.BaseRequestHandler):

    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def handle(self):
        handler = userHandler()
        user = ''
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        # Loop that listens for messages from the client
        while True:
            hasLoggedIn = False
            received_string = self.connection.recv(4096)
            if type(received_string) != str:
                received_string = self.connection.recv(4096)
                try:
                    jrec = json.loads(received_string)
                    body = jrec["content"].encode()
                    request = jrec["request"].encode()

                except ValueError:
                    print("Not JSON-Object, trying again.")
            else:
                jrec = json.loads(received_string)
                body = jrec["content"]
                request = jrec["request"]

            if request == 'login' and not hasLoggedIn:
                if handler.hasUser(body):
                    tid = time.time()
                    thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                    response = {"Timestamp": thisTime, "Sender": "Server", "Response": "Login", "Content": "The username is already in use, please choose another one."}
                    jsonresponse = json.dumps(response)
                    self.connection.send(json.dumps(jsonresponse))

                else:
                    handler.addConnection(self)
                    user = body
                    tid = time.time()
                    thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                    response = {"Timestamp": thisTime, "Sender": "Server", "Response": "Login", "Content": "Login Successful."}
                    jsonresponse = json.dumps(response)
                    self.connection.send(jsonresponse)
                    history = handler.getHistory()
                    for i in history:
                        self.connection.send(i)
                    print(body+" logged in.")
                    handler.addUser(str(body))
            elif request == 'logout':
                print handler.getUsers()
                print handler.getConnections()
                handler.removeUser(str(body))
                print(body+" logged out.")
                handler.removeConnection(self)
                tid = time.time()
                thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                obj = {"Timestamp": thisTime, "Sender": "Server", "Response": "Logout", "Content": "Logout successful"}
                self.connection.close()

            elif request == 'names':
                tid = time.time()
                thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                users = handler.getUsers()
                response = {"Timestamp": thisTime, "Sender": "Server", "Response": "Names", "Content": users}
                jsonresponse = json.dumps(response)
                self.connection.send(jsonresponse)
            elif request == 'history':
                    tid = time.time()
                    thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                    history = handler.getHistory()
                    response = {"Timestamp": thisTime, "Sender": "Server", "Response": "History", "Content": history}
                    jsonresponse = json.dumps(response)
                    self.connection.send(jsonresponse)
            elif request == 'msg':
                print("Got message: "+body)
                tid = time.time()
                thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                obj = {"Timestamp": thisTime, "Sender": user, "Response": "Message", "Content": body}
                jsonresponse = json.dumps(obj)
                handler.addMessage(jsonresponse)
                print("Added "+body+" to history")
                threads = handler.getConnections()
                tid = time.time()
                thisTime = datetime.datetime.fromtimestamp(tid).strftime('%H:%M:%S')
                response = {"Timestamp": thisTime, "Sender": user, "Response": "Message", "Content": body}
                jsonresponse = json.dumps(response)
                print threads
                for i in threads:
                        i.connection.send(jsonresponse)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations is necessary
    """


    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations is necessary
    """

    HOST, PORT = 'localhost', 20000
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
