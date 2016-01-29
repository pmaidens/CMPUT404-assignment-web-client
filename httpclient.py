#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Peter Maidens
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
    print "httpclient.py [URL] [GET/POST]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        return clientSocket

    def get_code(self, data):
        parsedData = re.search("HTTP\/\d.\d (\d{3}) [\w\W]+?\r?\n\r?\n", data)
        if parsedData == None:
            result = None
        else:
            result = int(float(parsedData.group(1)))
        return result

    def get_headers(self,data):
        return None

    def get_body(self, data):
        parsedData = re.search("[\w\W]+?\r?\n\r?\n([\w\W]+)", data)
        if parsedData == None:
            result = None
        else:
            result = parsedData.group(1)
        return result

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

    def parseUrl(self, url):
        parsedUrl = re.search("https?:\/\/([-a-zA-Z0-9@%._\+~#=]{2,256}(?:\.[a-z]{2,4})?)(?::([\d]+))?([-a-zA-Z0-9@:%_\+.~#&//=]*)?(\?[-a-zA-Z0-9@:%_\+.~#&//=]*)?", url)

        if parsedUrl.group(1) == None:
            host = ""
        else:
            host = parsedUrl.group(1)

        if parsedUrl.group(2) == None:
            port = "80"
        else:
            port = parsedUrl.group(2)

        if parsedUrl.group(3) == "" or parsedUrl.group(3) == None:
            resource = "/"
        else:
            resource = parsedUrl.group(3)

        return (host, int(float(port)), resource)

    def GET(self, url, args=None):
        (host, port, resource) = self.parseUrl(url)
        clientSocket = self.connect(host, port)
        request = "GET " + resource + " HTTP/1.1\r\n" \
                  "Host: " + host + "\r\n" \
                  "Connection: close\r\n" \
                  "Accept: text/plain;charset=UTF-8\r\n" \
                  "Accept-Charset: ISO-8859-1\r\n" \
                  "Content-Length: 0\r\n\r\n"
        clientSocket.sendall(request)

        response = self.recvall(clientSocket)

        return HTTPResponse(self.get_code(response), self.get_body(response))

    def POST(self, url, args=None):
        # code = 500
        # body = ""
        (host, port, resource) = self.parseUrl(url)
        clientSocket = self.connect(host, port)

        if args != None:
            body = urllib.urlencode(args)
            contentLength = len(body)
        else:
            body = ""
            contentLength = 0

        request = "POST " + resource + " HTTP/1.1\r\n" \
                  "Host: " + host + "\r\n" \
                  "Accept: */*\r\n" \
                  "Content-Length: " + str(contentLength) + "\r\n" \
                  "Content-Type: application/x-www-form-urlencoded\r\n\r\n" + body

        clientSocket.sendall(request)

        response = self.recvall(clientSocket)

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
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )
