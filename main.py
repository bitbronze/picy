from socketserver import ThreadingTCPServer, BaseRequestHandler
import base64, time



mountpoint_db = {}



class ExtendedBaseRequestHandler(BaseRequestHandler):

    def send_401(self):
        self.request.sendall(b'HTTP/1.1 401 Unauthorized\n')

    

    def parse_username_password_from_header_value(self, header_value):
        username_pass_base64 = header_value.split(' ')[1]
        username_pass_bytes = base64.b64decode(bytes(username_pass_base64, 'utf-8'))
        username_pass_list = username_pass_bytes.decode('utf-8').split(':')
        username = username_pass_list[0]
        password = username_pass_list[1]

        print(f"Client supplied the following credentials: username={username}, password={password}")

        return username, password
        


    def authenticate_client(self, username, password):
        # Not sure what to implement here but this is a placeholder

        if username == 'admin' and password == 'pass':
            return True
        else :
            return False



    def headers_to_dict(self, http_request_line_list):

        headers_dict = {}

        for line in http_request_line_list[1:]:
            line_split = line.split(":")
            headers_dict[line_split[0].strip()] = line_split[1].strip()

        return headers_dict



    def producer_loop(self, http_request_line_list, mountpoint):

        headers_dict = self.headers_to_dict(http_request_line_list)

        print("Headers: ")
        print(headers_dict)

        # First thing we should probably do is to verify the Authorization header to authenticate the client
        username, password = self.parse_username_password_from_header_value(headers_dict['Authorization'])
        auth_passed = self.authenticate_client(username, password)

        if not auth_passed:
            print("Producer failed authentication")
            self.send_401()
            return
        else:
            print("Producer passed authentication")


        # We will load relavent data form the request into our dict of active mountpoints and their data.
        mountpoint_db[mountpoint] = {
            "ice-name" : headers_dict['ice-name'],
            "ice-description" : headers_dict['ice-description'],
            "stream_data" : bytearray([]),
            "stream_data_sequence_number" : 0
        }


        # Do PUT / PRODUCER processing:
        self.request.sendall(b'HTTP/1.1 100 Continue\n')
        self.request.sendall(b'Server: Picy 0.0.1\n')

        try:
            while True:
                data = self.request.recv(4096)
                if data == b'':
                    print("Producer disconnected?")
                    break
                mountpoint_db[mountpoint]['stream_data'] = data
                mountpoint_db[mountpoint]['stream_data_sequence_number'] += 1
                print(mountpoint_db[mountpoint]['stream_data_sequence_number'])
        except Exception as e:
            print(e)

        #mountpoint_db.remove(mountpoint)


    def consumer_loop(self, http_request_line_list, mountpoint):

        if mountpoint in mountpoint_db:

            self.request.sendall(b"HTTP/1.1 200 OK\n")
            self.request.sendall(b"Content-Type: audio/mpeg\n")
            self.request.sendall(b"Ice-Audio-Info: ice-samplerate=48000;ice-bitrate=320;ice-channels=2\n")
            self.request.sendall(b"Ice-Bitrate: 320\n")
            self.request.sendall(b"Connection: keep-alive\n")
            self.request.sendall(b"Access-Control-Allow-Origin: *\n\n")


            curr_seq_num = mountpoint_db[mountpoint]['stream_data_sequence_number']
            while True:
                if not curr_seq_num == mountpoint_db[mountpoint]['stream_data_sequence_number']:
                    curr_seq_num = mountpoint_db[mountpoint]['stream_data_sequence_number']
                    self.request.sendall(mountpoint_db[mountpoint]['stream_data'])



    def handle(self):


        print("")


        # New client has connected.
        print(f"New connection from {self.client_address}.")

        # Read the first chunk of the request sent by the new client.
        time.sleep(0.1)
        recv_data = self.request.recv(1024).strip()

        # HTTP parsing
        http_request = recv_data.decode('utf-8')
        print(http_request)
        http_request_line_list = http_request.split('\n')

        request_banner = http_request_line_list[0]          # PUT /song.mp3 HTTP/1.1
        http_verb      = request_banner.split(" ")[0]       # PUT
        mountpoint     = request_banner.split(" ")[1]       # /song.mp3

        print(http_verb)
        if http_verb == "PUT":
            print("Client is a producer?")
            self.producer_loop(http_request_line_list, mountpoint)

        if http_verb == "GET":
            print("Client is a consumer?")
            self.consumer_loop(http_request_line_list, mountpoint)        
        

        print("")



server = ThreadingTCPServer(("0.0.0.0", 80), ExtendedBaseRequestHandler)
print("Starting server...")
server.serve_forever()
    