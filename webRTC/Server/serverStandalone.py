# The MIT License (MIT)

# Copyright (c) 2015 

# John Congote <jcongote@gmail.com>
# Felipe Calad
# Isabel Lozano
# Juan Diego Perez
# Joinner Ovalle

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from tornado.websocket import WebSocketHandler
from tornado.httpserver import HTTPServer
import uuid

global_rooms = {}

class Room(object):
    def __init__(self, name, clients=[]):
        self.name = name
        self.clients = clients
    def __repr__(self):
        return self.name

class HelloHandler(RequestHandler):
    def get(self):
        room = str(uuid.uuid4())
        self.write(room)
        
class NewWS(WebSocketHandler):
    def open(self,slug):
        if slug in global_rooms:
            global_rooms[slug].clients.append(self)
        else:
            global_rooms[slug] = Room(slug,[self])
        self.room = global_rooms[slug]
        if len(self.room.clients) > 2:
            self.write_message('fullhouse')
        elif len(self.room.clients) == 1:
            self.write_message('initiator')
        else:
            self.write_message('not initiator')           
        print "WebSocket opened"

    def on_message(self, message):
        # self.write_message("You said: " + message)
        for client in self.room.clients:
            if client is self:
                continue
            client.write_message(message)

    def on_close(self):
        self.room.clients.remove(self)
        print "WebSocket closed"
    
    def check_origin(self, origin):
        return True
    
def make_app():
    return Application([
        url(r"/", HelloHandler),
        url(r'/ws/([^/]*)', NewWS),
        # url(r'/ws/([^/]*)', EchoWebSocket)
        ])

def main():
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(7000)
    print "Running in the port 7000"
    IOLoop.current().start()
    
if __name__ == '__main__':
    main()
