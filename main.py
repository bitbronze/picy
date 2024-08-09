from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer



class ExtendedBaseHTTPRequestHandlerClass(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"New connection from {self.client_address}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<html><head></head><body>OK!</body></html>")

    def do_SOURCE(self):
        print(f"New SOURCE connection from {self.client_address}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"response":"ok"}')



server = ThreadingHTTPServer(("0.0.0.0", 80), ExtendedBaseHTTPRequestHandlerClass)
server.serve_forever()