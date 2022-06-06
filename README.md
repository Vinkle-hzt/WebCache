# WebCache

## 开发环境

Windows 10

python 3.7.9

## 项目结构

├── **cache**                                 缓存文件夹

├── main.py                              main 函数

└── web_proxy.py                    web proxy server

## 运行项目

```
python -u main.py [-h] [--port PORT]

optional arguments:
  -h, --help   show this help message and exit
  --port PORT  port number
```

## 项目功能

### 基本cache功能

#### 第一次获取文件：转发请求，并将相应存入 `cache`

使用 `curl` 获取本地服务器的 `test.png` 文件

```bash
curl 127.0.0.1:8000/test.png --output file1.png --proxy 127.0.0.1:18080
```

文件成功返回

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  3543  100  3543    0     0   154k      0 --:--:-- --:--:-- --:--:--  164k
```

web cache server 信息

```
Web Proxy starting on port: 18080...
received request: 
 GET http://127.0.0.1:8000/test.png HTTP/1.1
Host: 127.0.0.1:8000
User-Agent: curl/7.83.1
Accept: */*
Proxy-Connection: Keep-Alive



received HTTP GET request:
request_file:  /test.png
url:  http://127.0.0.1:8000/test.png
request host:  127.0.0.1
request port:  8000
cache_path:  cache/MTI3LjAuMC4x/aHR0cDovLzEyNy4wLjAuMTo4MDAwL3Rlc3QucG5n
searching in the cache...
not find in cache, send request to server.

find content-length:  3543

LEN of response_data:  0 / 3543
LEN of response_data:  1024 / 3543
LEN of response_data:  2048 / 3543
LEN of response_data:  3072 / 3543
LEN of response_data:  3543 / 3543
finish receiving response data.

send response to client...
finish sending response to client.
close connection.

save response to cache.
```

可以看出，`web cache server` 先会查找 `cache`，如果不存在，转发 `http request`，再将收到的 `http response` 转发回 `client`，并将内容存储到 `cache` 中。

`wireshark` 抓包信息，符合预期

![image-20220606112403525](C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606112403525.png)

查看获取文件和源文件属性，数据一致，说明文件获取没有问题

<table rules="none" align="center">
	<tr>
		<td>
			<center>
				<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606113121750.png" width="60%" />
				<br/>
				<font color="AAAAAA">源文件属性</font>
			</center>
		</td>
		<td>
			<center>
				<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606113146369.png" width="60%" />
				<br/>
				<font color="AAAAAA">获取到的文件属性</font>
			</center>
		</td>
	</tr>
</table>

#### 第二次获取文件：发送 `conditional GET`，无修改返回 `cache`

使用 `curl` 获取本地服务器的 `test.png` 文件

```bash
curl 127.0.0.1:8000/test.png --output file2.png --proxy 127.0.0.1:18080 
```

文件成功返回

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  3543  100  3543    0     0   174k      0 --:--:-- --:--:-- --:--:--  182k
```

`web cache server` 信息

```
received request:
 GET http://127.0.0.1:8000/test.png HTTP/1.1
Host: 127.0.0.1:8000
User-Agent: curl/7.83.1
Accept: */*
Proxy-Connection: Keep-Alive



received HTTP GET request:
request_file:  /test.png
url:  http://127.0.0.1:8000/test.png
request host:  127.0.0.1
request port:  8000
cache_path:  cache/MTI3LjAuMC4x/aHR0cDovLzEyNy4wLjAuMTo4MDAwL3Rlc3QucG5n
searching in the cache...
found in the cache!
cache Date:  Mon, 06 Jun 2022 03:14:58 GMT
send conditional get request...
get response not modified
send cache to client...
```

可以看出，`web cache server` 先查找 `cache`，再根据 `cache` 中的 `Date` 字段数据发送 `conditional GET` 请求，`web cache server` 接收到服务器的 `HTTP 304 Not Modified` 回复后，发送 `cache` 至 `client`。

`wireshark` 抓包信息，符合预期

![image-20220606114737379](C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606114737379.png)

`conditional GET` 信息，符合预期

<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606114821304.png" alt="image-20220606114821304" style="zoom:50%;" />

查看获取文件和源文件属性，数据一致，说明文件获取没有问题

<table rules="none" align="center">
	<tr>
		<td>
			<center>
				<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606113121750.png" width="60%" />
				<br/>
				<font color="AAAAAA">源文件属性</font>
			</center>
		</td>
		<td>
			<center>
				<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606121301985.png" width="60%" />
				<br/>
				<font color="AAAAAA">获取到的文件属性</font>
			</center>
		</td>
	</tr>
</table>

### 采用condition GET 更新 cache

修改 `127.0.0.1:8000/test.png` 文件

再使用 `curl` 获取本地服务器的 `test.png` 文件

```bash
curl 127.0.0.1:8000/test.png --output file3.png --proxy 127.0.0.1:18080
```

文件成功返回

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  175k  100  175k    0     0  1971k      0 --:--:-- --:--:-- --:--:-- 1989k
```

`web cache server` 信息

```
received HTTP GET request: 
request_file:  /test.png
url:  http://127.0.0.1:8000/test.png
request host:  127.0.0.1
request port:  8000
cache_path:  cache/MTI3LjAuMC4x/aHR0cDovLzEyNy4wLjAuMTo4MDAwL3Rlc3QucG5n
searching in the cache...
found in the cache!
cache Date:  Mon, 06 Jun 2022 03:14:58 GMT
send conditional get request...
find content-length:  179276 

LEN of response_data:  0 / 179276
LEN of response_data:  1024 / 179276
LEN of response_data:  2048 / 179276
LEN of response_data:  3072 / 179276
LEN of response_data:  4096 / 179276
...(内容太多，省略了)
LEN of response_data:  176128 / 179276
LEN of response_data:  177152 / 179276
LEN of response_data:  178176 / 179276
LEN of response_data:  179200 / 179276
LEN of response_data:  179276 / 179276
finish receiving response data.

get response modified
send response to client...
rewrite the cache.
```

可以看出，`web cache server` 先查找 `cache`，再根据 `cache` 中的 `Date` 字段数据发送 `conditional GET` 请求，由于文件已经更改，服务器重新发送文件，`web cache server` 接受文件后转发回 `client` 并重新写入 `cache`。

`wireshark` 抓包信息，符合预期

![image-20220606122154160](C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606122154160.png)

`conditional GET` 请求信息，符合预期

<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606122233376.png" alt="image-20220606122233376" style="zoom:50%;" />

`conditional GET` 回复信息，符合预期

<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606122301707.png" alt="image-20220606122301707" style="zoom:50%;" />

查看获取文件和源文件属性，数据一致，说明文件获取没有问题

<table rules="none" align="center">
	<tr>
		<td>
			<center>
				<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606122623499.png" width="60%" />
				<br/>
				<font color="AAAAAA">源文件属性</font>
			</center>
		</td>
		<td>
			<center>
				<img src="C:\Users\vinkle\AppData\Roaming\Typora\typora-user-images\image-20220606122601196.png" width="60%" />
				<br/>
				<font color="AAAAAA">获取到的文件属性</font>
			</center>
		</td>
	</tr>
</table>

## 项目文档

### main.py

```python
if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18080, help='port number')
    args = parser.parse_args()

    # start proxy server
    web_proxy.proxy_server(args)
```

处理命令行参数，运行`web cache(proxy) server`

### web_proxy.py

`proxy_server` 类：运行 `web cache`

#### 初始化函数

```python
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
```

使用 `socket` 创建 `cache server` 监听请求，收到请求后创建新线程处理请求

#### 请求处理函数

```python
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
```

分析请求的HTTP头部信息，根据请求类型调用不同的处理函数

#### 解析HTTP Request

```python
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
```

用于解析HTTP协议字段信息

#### 转发 request 请求

```python
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
```

转发 `request` 请求步骤：

- 创建和服务器的 `socket` 连接
- 转发 `request`
- 获取服务器的 `response`
- 转发服务器的 `response` 至 `client`

#### 获取 response

```python
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
```

获取 `response` 步骤：

- 判断 `HTTP code` 是否为 `304`，是则返回 `None`，代表不需要更新 `cache`
- 判断 `HTTP Header` 是否接受完毕，接受完毕后，解析 `HTTP Header` 查找 `Content-Length` 字段并记录
- 判断当前接受的数据长度是否达到 `content-lenth`，达到代表 `response` 接收结束。
- 返回 `response`

#### 处理HTTP GET请求

```python
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
```

处理 `GET` 请求步骤：

- 解析 `HTTP Request`
- 根据 `request file` 和 `request (host:port)` 来确认 `cache` 位置，采用 `base64` 编码来避免非法字符
- 若寻找到 `cache` 文件
  - 解析获得 `cache` 文件中的 `Date` 信息，作为 `Conditional GET` 中的 `If-Modified-Since` 字段内容
  - 发送 `Conditional GET`
  - 接受 `Conditional GET` 的 `response` 信息
  - 如果接受到 `HTTP 304` 则直接返回 `cache`，否则返回 `response` 并更新 `cache`
- 若没有找到 `cache` 文件
  - 转发 `HTTP Request` 至目标服务器
  - 接受服务器的 `response` 并解析
  - 如果获得 `HTTP 200`，则存入 `cache`
