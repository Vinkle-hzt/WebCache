import web_proxy;
import argparse;

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18080, help='port number')
    args = parser.parse_args()

    # start proxy server
    web_proxy.proxy_server(args)

