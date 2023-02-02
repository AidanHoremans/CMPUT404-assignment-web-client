#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Aidan Horemans
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

GET = "GET"
POST = "POST"
HTTPVERSION = "HTTP/1.1"
PORT = 80

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPRequest(object):
    def __init__(self, method: str, host: str, path: str, query: str, body: str):
        path = path or "/"
        
        userAgent = "User-Agent: curl/7.83.1"

        if query:
            query = "?" + query

        self.body = f"{method} {path}{query} {HTTPVERSION}\r\nHost: {host}\r\n{userAgent}\r\nAccept: */*\r\nContent-Length: {len(body)}\r\n"

        if body:
            self.body += f"Content-Length: {len(body)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{body}"
        else:
            self.body += f"\r\n\r\n" # empty body


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    
    def __str__(self):
        return f"{self.code} {self.body}"

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(5)
        print(f"Connecting from: {self.socket.getsockname()}")
        print(f"Connecting to: {self.socket.getpeername()}")
        return None

    # read through values from recvall, and parse the data out here
    def get_code(self, data: str):
        if not data:
            return None

        split = data.splitlines()
        if len(split) == 0:
            return None

        response = split[0].split() #get code out
        if len(response) < 2:
            return None

        try:
            code = int(response[1]) #if not a valid int, return
        except:
            return None

        return code

    def get_headers(self, data):
        
        return None

    def get_body(self, data):
        splitData = data.split('\r\n\r\n')
        body = ""
        if len(splitData) == 2:
            body = splitData[1]
        return body

    # --------

    def parse_url(self, url):
        parsedUrl = urllib.parse.urlsplit(url)
        return parsedUrl.hostname, parsedUrl.port, parsedUrl.path, parsedUrl.query

    def sendall(self, data: str):
        self.socket.sendall(data.encode('utf-8'))
        #self.socket.shutdown(socket.SHUT_WR) #tell server we're done talking
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock: socket.socket):
        buffer = bytearray()

        done = False
        while not done:
            try:
                part = sock.recv(1024) # need some way to break from this once no more data
            except:
                return buffer.decode('utf-8')
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path, query = self.parse_url(url)

        body = ""

        if args:
            for arg, val in dict(args).items():
                if not body:
                    body += f"{arg}={val}"
                else:
                    body += f"&{arg}={val}"

        request = HTTPRequest(GET, host, path, query, body)

        self.connect(host, port or PORT)
        print(f"REQUEST\n{request.body}")
        self.sendall(request.body)
        response = self.recvall(self.socket)
        print(f"RESPONSE\n{response}")
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path, query = self.parse_url(url)

        body = ""

        if args:
            for arg, val in dict(args).items():
                if not body:
                    body += f"{arg}={val}"
                else:
                    body += f"&{arg}={val}"

        request = HTTPRequest(POST, host, path, query, body)

        self.connect(host, port or PORT)
        print(f"REQUEST\n{request.body}")
        self.sendall(request.body)
        response = self.recvall(self.socket)
        print(f"RESPONSE\n{response}")
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))