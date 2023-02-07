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

        self.body = f"{method} {path}{query} {HTTPVERSION}\r\nHost: {host}\r\n{userAgent}\r\nAccept: text/*; charset=UTF-8\r\nContent-Length: {len(body)}\r\nConnection: close\r\n"

        if body:
            self.body += f"Content-Type: application/x-www-form-urlencoded\r\n\r\n{body}"
        else:
            self.body += f"\r\n\r\n" # empty body


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    
    def __str__(self):
        return f"---RESPONSE---\nCode:{self.code}\nBody:\n{self.body}"

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(4) #timeout of 4 seconds in case connection gets stuck
        print(f"Connecting from: {self.socket.getsockname()}") #for sanity
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

    def get_body(self, data):
        splitData = data.split('\r\n\r\n')
        body = ""
        if len(splitData) >= 2: #if there are more than 1 \r\n\r\n in the response, just parse from the first (all others are assumed to be part of body)
            for data in splitData[1:]:
                body += data
        return body

    # --------

    def parse_url(self, url):
        parsedUrl = urllib.parse.urlsplit(url)
        return parsedUrl.scheme, parsedUrl.hostname, parsedUrl.port, parsedUrl.path, parsedUrl.query

    def sendall(self, data: str):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock: socket.socket):
        buffer = bytearray()

        while True:
            try:
                part = sock.recv(1024)
            except:
                break

            if (part):
                buffer.extend(part)
            else:
                break

        try:
            return buffer.decode('utf-8')
        except:
            return buffer.decode('ISO-8859-1') #some sites return non utf-8 even though we explicitly ask for it? better safe than sorry

    def GET(self, url, args=None):
        scheme, host, port, path, query = self.parse_url(url)

        if scheme != "http":
            print("Only http:// requests are accepted")
            return

        body = ""

        # if we were parsed args, add them to the query parameters if they exist, otherwise set them as the query parameters
        if args:
            parsedArgs = urllib.parse.urlencode(args)
            if query:
                query += f"&{parsedArgs}"
            else:
                query = parsedArgs

        request = HTTPRequest(GET, host, path, query, body)

        self.connect(host, port or PORT)
        print(f"---REQUEST---\n{request.body}")
        self.sendall(request.body)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        scheme, host, port, path, query = self.parse_url(url)

        if scheme != "http":
            print("Only http:// requests are accepted")
            return

        body = ""

        if args:
            body = urllib.parse.urlencode(args)

        request = HTTPRequest(POST, host, path, query, body)

        self.connect(host, port or PORT)
        print(f"---REQUEST---\n{request.body}")
        self.sendall(request.body)
        response = self.recvall(self.socket)
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