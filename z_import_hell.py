from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn


class ExtendedRequestHandlerClass(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"New connection from {self.client_address}")
        self.send_response(200)
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer): # What is this building and how can it work like this??? (Aparently its multi-deriving this class from two classes)
    pass

server = ThreadedHTTPServer(("0.0.0.0", 8000), ExtendedRequestHandlerClass) # Why can I simply do this then??? (Aparently the arguments go to HTTPServer's init method, ThreadingMixIn is just mixin, it overrides some functionality but it dosent have a init method)
server.serve_forever()

# So many questions so little answers...