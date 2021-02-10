#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    # get IP of host, taken from Lab 2, unchanged if host is already IP
    def get_remote_ip(self, host):
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting...")
            sys.exit()
        return remote_ip

    # convert POST data from dict to POST body format, returns '' if there is
    # no POST data
    def get_post_body(self, data):
        body = []
        if data:
            for key in sorted(data):
                body.append(f"{key}={data[key]}")
        return '&'.join(body)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # get IP of host
        host = self.get_remote_ip(host)
        self.socket.connect((host, port))
        return None

    # split response to get HTTP status code
    def get_code(self, data):
        data = data.split('\r\n\r\n')
        header = data[0]
        body = data[1]

        status_line = header.split('\r\n')[0]
        code = int(status_line.split()[1])

        return code

    # split response to get HTTP header
    def get_headers(self, data):
        data = data.split('\r\n\r\n')
        header = data[0]
        return header

    # split response to get HTTP body
    def get_body(self, data):
        data = data.split('\r\n\r\n')
        body = data[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8', "replace")

    def GET(self, url, args=None):
        code = 500
        body = ""
        port = 80
        path = '/'
        # using urllib.parse to parse url
        o = urllib.parse.urlparse(url)
        # if no port is specified, it will be None, default to port 80 for HTTP
        if o.port:
            port = o.port
        # if no path is specified, it will be None, default to '/'
        if o.path:
            path = o.path

        self.connect(o.hostname, port)

        # request header
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {o.netloc}\r\n"
            f"User-Agent: CMPUT 404 HTTP Client\r\n"
            f"Connection: close\r\n"
            f"Accept: */*\r\n\r\n"
        )

        # send response, recieve request close socket
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)

        # print result to stdout
        print(header + '\n')
        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        port = 80
        path = '/'
        # using urllib.parse to parse url
        o = urllib.parse.urlparse(url)
        # if no port is specified, it will be None, default to port 80 for HTTP
        if o.port:
            port = o.port
        # if no path is specified, it will be None, default to '/'
        if o.path:
            path = o.path

        self.connect(o.hostname, port)

        # convert to POST body format and count length in byte
        # length = 0 if no POST data
        request_body = self.get_post_body(args)
        length = len(request_body.encode('utf-8'))

        header = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {o.netloc}\r\n"
            f"User-Agent: CMPUT 404 HTTP Client\r\n"
            f"Connection: close\r\n"
            f"Accept: */*\r\n"
            f"Content-Length: {length}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n\r\n"
        )

        # send response, recieve request close socket
        request = header + request_body
        self.sendall(request)
        response = self.recvall(self.socket)

        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)
        
        # print result to stdout
        print(header + '\n')
        print(body)
        
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
