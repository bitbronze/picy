from socketserver import ThreadingTCPServer, BaseRequestHandler
import base64, time



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



class ExtendedBaseRequestHandler(BaseRequestHandler):


    def handle(self):


        print("")


        # New client has connected.
        print(f"New connection from {self.client_address}.")
        time.sleep(0.1)

        # Read the first chunk of the request sent by the new client.
        recv_data = self.request.recv(1024).strip()

        # HTTP parsing
        http_request = recv_data.decode('utf-8')
        print(http_request)
        http_request_line_list = http_request.split('\n')

        request_banner = http_request_line_list[0]

        http_verb = request_banner.split(" ")[0]
        mountpoint = request_banner.split(" ")[1]

        print(http_verb)
        print(mountpoint)
        


        return


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


        # We will load relavent data form the request into our list of active mountpoints and their data.
        mountpoint_data = {
            "mountpoint" : self.path,
            "ice-name" : self.headers['ice-name'],
            "ice-description" : self.headers['ice-description']
        }
        mountpoint_db.append(mountpoint_data)


        # Respond with good words to soften the heart (purse) of the client
        self.send_response(100)
        self.send_header("Server", "Picy 0.0.1")
        self.end_headers()
        time.sleep(1)



        mountpoint_db.remove(mountpoint_data)
        print("")



server = ThreadingTCPServer(("0.0.0.0", 80), ExtendedBaseRequestHandler)
print("Starting server...")
server.serve_forever()
    