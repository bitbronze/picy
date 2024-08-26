from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64

mountpoint_db = []

def parse_username_password_from_header_value(header_value):
    username_pass_base64 = header_value.split(' ')[1]
    username_pass_bytes = base64.b64decode(bytes(username_pass_base64, 'utf-8'))
    username_pass_list = username_pass_bytes.decode('utf-8').split(':')
    username = username_pass_list[0]
    password = username_pass_list[1]

    print(f"Client supplied the following credentials: username={username}, password={password}")

    return username, password
    


def authenticate_client(username, password):
    # IDK what to implement here but rest assured this function is a placeholder

    if username == 'admin' and password == 'pass':
        return True
    else :
        return False



class ExtendedBaseHTTPRequestHandlerClass(BaseHTTPRequestHandler):

    def do_PUT(self):

        print("")

        # New client has connected.

        # At this point we have no idea what he is or what he wants to do.
        print(f"New client connection from {self.client_address} Producer? Mountpoint recognised as {self.path}")
        print("Headers: ")
        print(self.headers)

        # First thing we should probably do is to verify the Authorization header to authenticate the client
        username, password = parse_username_password_from_header_value(self.headers['Authorization'])
        auth_passed = authenticate_client(username, password)

        if not auth_passed:
            print("Producer failed authentication")
            self.send_response(401)
            self.end_headers()
            return
        else:
            print("Producer passed authentication")


        mountpoint_data = {
            "mountpoint" : self.path,
            "ice-name" : self.headers['ice-name'],
            "ice-description" : self.headers['ice-description']
        }
        mountpoint_db.append(mountpoint_data)


        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<html><head></head><body>OK!</body></html>")



        mountpoint_db.remove(mountpoint_data)
        print("")



server = ThreadingHTTPServer(("0.0.0.0", 80), ExtendedBaseHTTPRequestHandlerClass)
print("Starting server...")
server.serve_forever()
    