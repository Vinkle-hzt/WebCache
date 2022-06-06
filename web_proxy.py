import http
import os
import socket
import sys
import base64
import threading


class proxy_server:
    def __init__(self, args) -> None:
        # message
        print('Web Proxy starting on port: %i...' % (args.port))

        # create proxy server
        proxySever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind port
        try:
            proxySever.bind(("", args.port))
        except:
            sys.exit("proxy bind error")

        # listen connection
        proxySever.listen(1024)

        while True:
            conn, addr = proxySever.accept()
            # use thread to handle request
            threading.Thread(target=self.handle_request, args=(conn,)).start()


    def handle_request(self, conn):
        # receive request
        request = conn.recv(1024).decode()
        print("received request: \n", request)
        request_type = request.split(' ')[0]
        if request_type == 'GET':
            # get request
            self.get_request(conn, request)
        else:
            # other request
            self.other_request(conn, request)


    def get_request(self, conn, request):
        request, request_host, request_port, request_file, request_url = self.deal_request(request)

        # define cache path cache/base64(host:port)/base64(request_url)
        cache_dirname = "cache/" + base64.encodestring(request_host.encode()).decode().strip()
        cache_filename = base64.encodestring(request_url.encode()).decode().strip()
        cache_path = cache_dirname + "/" + cache_filename

        # show request
        print("\nreceived HTTP GET request: ")
        print("request_file: ", request_file)
        print("url: ", request_url)
        print("request host: ", request_host)
        print("request port: ", request_port)
        print("cache_path: ", cache_path)
        

        print("searching in the cache...")
        try:
            cache = None
            # try find the cache
            with open(cache_path, 'rb') as f:
                # get cache
                print("found in the cache!")
                cache = f.read()
                f.close()

            # get cache Date
            date_idx = cache.find(b'Date: ')
            date = cache[date_idx+6:].split(b'\r\n')[0].decode().strip()
            print("cache Date: ", date)

            # conditional get request
            request_header = request.split('\r\n\r\n')[0]
            request_data = request[request.find('\r\n\r\n')+4:]
            request = request_header + '\r\nIf-Modified-Since: ' + date + '\r\n\r\n' + request_data

            # do conditional get
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((request_host, request_port))
            server.sendall(request.encode())
            print("send conditional get request...")
            response = self.get_response_from_server(server)

            # deal with conditional get response
            if response is None:
                # not modified
                print("get response not modified")
                print("send cache to client...")
                conn.sendall(cache)
            else:
                # modified
                print("get response modified")
                # send response to client
                print("send response to client...")
                conn.sendall(response)
                # save cache
                with open(cache_path, 'wb') as f:
                    print("rewrite the cache.")
                    f.write(response)
                    f.close()

        except FileNotFoundError:
            # if not find in cache, send request to server
            print("not find in cache, send request to server.\n")
            response = self.forward_to_server(conn, request, request_host, request_port)

            http_code = response.split(b'\r\n')[0].split(b' ')[1].decode()
            if http_code == '200':
                # save response to cache
                has_dir = os.path.exists(cache_dirname)
                if not has_dir:
                    os.makedirs(cache_dirname)
                with open(cache_path, 'wb') as f:
                    f.write(response)
                    f.close()
                    print("save response to cache.\n")
            else:
                print("get error http code: ", http_code)
                print("not save response to cache.\n")


    def forward_to_server(self, conn, request, request_host, request_port):
        # forward request to server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((request_host, request_port))
        server.sendall(request.encode())

        # get response from server
        response = self.get_response_from_server(server)
        print("send response to client...")
        # print(response)

        # send response to client
        conn.sendall(response)
        print("finish sending response to client.")
        print("close connection.\n")

        # close connection
        server.close()
        return response


    def get_response_from_server(self, server):
        # receive response from server
        response = b''
        response_header = b''
        response_data = b''
        get_data = False
        content_length = -1

        while True:
            data = server.recv(1024)
            if data == b'':
                break
            response += data

            # if not modify return cache
            if len(data.split(b' ')) > 1:
                if b'304' == data.split(b' ')[1]:
                    return None

            # get response header finished
            if b'\r\n\r\n' in data:
                get_data = True
            
            # get response data
            if get_data:
                # first get data
                if response_header == b'':
                    # get response header
                    header_index = response.find(b'\r\n\r\n')
                    response_header = response[:header_index]
                    # if has content-length
                    if b'Content-Length' in response_header:
                        # get content-length
                        content_length_idx = response_header.find(b'Content-Length')
                        content_length = int(response_header[content_length_idx:].split(b'\r\n')[0].split(b':')[1].decode().strip())

                        print("find content-length: ", content_length, "\n")
                        # init response data
                        response_data = response[header_index+4:]
                    # not has content-length just break
                    else:
                        break
                # get data normally
                else:
                    response_data += data

                if content_length != -1:
                    print("LEN of response_data: ", len(response_data), "/", content_length)
                    if len(response_data) == content_length:
                        print("finish receiving response data.\n")
                        break

        return response


    def other_request(self, conn, request):
        # just forward request to server
        request, request_host, request_port, _, _ = self.deal_request(request)
        response = self.forward_to_server(conn, request, request_host, request_port)
        conn.sendall(response)


    def deal_request(self, request):
        # define url and host
        request_url = request.split(' ')[1].strip()
        request_host = request.split('\r\n')[1].split(' ')[1].strip()
        request_file = request_url.replace('http://' + request_host, '').strip()
        if (len(request_file) == 0):
            request_file = '/'
        request = request.replace(request_url, request_file)

        # define port
        request_port = 80
        if ':' in request_host:
            request_port = int(request_host.split(':')[1])
            request_host = request_host.split(':')[0]

        return request, request_host, request_port, request_file, request_url
