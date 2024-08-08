from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer



class ExtendedRequestHandlerClass(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"New connection from {self.client_address}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<html><head></head><body>OK!</body></html>")



server = ThreadingHTTPServer(("0.0.0.0", 80), ExtendedRequestHandlerClass)
server.serve_forever()