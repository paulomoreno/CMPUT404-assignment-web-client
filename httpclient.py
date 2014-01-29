#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle

# Copyright 2014 Paulo H. O. Moreno

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
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def get_body(self):
        return self.body

    def get_code(self):
        return self.code

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        try:
            #create an AF_INET, STREAM socket (TCP)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print ('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
            sys.exit();
        try:
            remote_ip = socket.gethostbyname( host )
        except socket.gaierror:
            #could not resolve
            print ('Hostname \'' + host + '\' could not be resolved. Exiting')
            sys.exit()
        #Connect to remote server
        sock.connect((remote_ip , port))
        return sock

    def get_code(self, data):
        return int(data.split(' ',2)[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split('\r\n\r\n',2)[1]

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
        return str(buffer)

    def GET(self, url, args=None):
        aux = self.assemble_header("GET",url)

        host = aux[0]
        port = aux[1]
        header = aux[2]

        #Send request
        sock = self.connect(host, port)
        #print("\n----\nRequest:\n----\n" + header + "\n\n")
        sock.sendall(header.encode("UTF8"))

        response = self.recvall(sock)
        #print("\n----\nResponse:\n----\n" + response + "\n\n")

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        body = self.assemble_body(args)

        aux = self.assemble_header("POST",url, len(body))

        host = aux[0]
        port = aux[1]
        header = aux[2]

        #Send request
        sock = self.connect(host, port)
        #print("\n----\nRequest:\n----\n" + header + "\n\n")
        sock.sendall(header.encode("UTF8"))
        if len(body) > 0:
                    sock.sendall(body)

        response = self.recvall(sock)
        #print("\n----\nResponse:\n----\n" + response + "\n\n")

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):

        if (command == "POST"):
            resp = self.POST( url, args )
        else:
            resp = self.GET( url, args )

        if resp.get_code() == 200:
            return resp
        if resp.get_code() == 404:
            print('Error 404: Not found!')
            return None
        else:
            return None

    def assemble_header(self, type, url, length=0):

        return_args = self.url_analysis(url)

        s_url = return_args.pop()
        host = return_args[0]
        port = return_args[1]

        header = type + " " + s_url + " HTTP/1.1\r\n"
        if port != 80:
            header += "Host: " + host + ":" + str(port) + "\r\n"
        else:
            header += "Host: " + host + "\r\n"
        header += "User-Agent: UofA CMPUT410 HTTPClient (Ubuntu 12.04 compatible) \r\n"
        if type == 'POST':
            header += "Content-Length: " + str(length) + "\r\n"
            if length > 0:
                            header += "Content-Type: application/x-www-form-urlencoded\r\n"

        header += "Connection: \"close\"\r\n\r\n"


        return_args.append(header)

        return return_args

    def assemble_body(self, args):
        if args:
            return urllib.urlencode(args)
        else:
            return ''


    def url_analysis(self, url):
        host = ""
        s_url = ""
        port = 80

        return_args = []

        #analyze the url
        if url:
            url = url.lstrip("http://")
            url = url.lstrip("HTTP://")

            #find the host
            host = re.findall('[^/]+',url)[0]

            #find the rest
            s_url = url.lstrip(host)

        if len(s_url) == 0:
            s_url += "/"

        if ':' in host:
            aux = host.split(':')
            host = aux[0]
            port = int(aux[1])

        return_args.append(host)
        return_args.append(port)
        return_args.append(s_url)

        return return_args

    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        resp = client.command( sys.argv[2], sys.argv[1] )
    else:
        resp = client.command( sys.argv[1], command )   

    if resp:
        print(resp.get_body())
