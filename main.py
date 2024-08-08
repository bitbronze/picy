from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer



class ExtendedRequestHandlerClass(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"New connection from {self.client_address}")
        self.send_response(200)
        self.end_headers()



server = ThreadingHTTPServer(("0.0.0.0", 8000), ExtendedRequestHandlerClass)
server.serve_forever()