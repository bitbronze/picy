from socketserver import ThreadingTCPServer, BaseRequestHandler
import logging
import base64, time
import ringbuffer


mountpoint_db = {}



class ExtendedBaseRequestHandler(BaseRequestHandler):



    def error_out(self):
        self.request.sendall(b'HTTP/1.1 401 Unauthorized\r\n')
        self.request.sendall(b'\r\n')



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



    def producer_flow(self, http_request_line_list, mountpoint):

        headers_dict = self.headers_to_dict(http_request_line_list)

        #print("Headers: ")
        #print(headers_dict)

        # First thing we should probably do is to verify the Authorization header to authenticate the client
        username, password = self.parse_username_password_from_header_value(headers_dict['Authorization'])
        auth_passed = self.authenticate_client(username, password)

        if not auth_passed:
            print("Producer failed authentication")
            self.error_out()
            return
        else:
            print("Producer passed authentication")


        # We will load relevant data from the request into our dict of active mountpoints and their data.
        mountpoint_db[mountpoint] = {
            "ice-name" :        headers_dict['ice-name']        if ('ice-name' in headers_dict)        else "Unknown",
            "ice-description" : headers_dict['ice-description'] if ('ice-description' in headers_dict) else "Unknown",
            "ringbuffer" : ringbuffer.RingBuffer(slot_bytes=2048, slot_count=100)
        }

        #print(mountpoint_db)

        # Do PUT / PRODUCER processing:
        self.request.sendall(b'HTTP/1.1 100 Continue\r\n')
        self.request.sendall(b'Server: Picy 0.0.1\r\n')
        self.request.sendall(b"\r\n")

        ring_buffer : ringbuffer.RingBuffer = mountpoint_db[mountpoint]['ringbuffer']
        ring_buffer.new_writer()


        while True:

            #data = self.request.recv(32768)

            def myreceive():
                chunks = []
                bytes_recd = 0
                while bytes_recd < 2048:
                    chunk = self.request.recv(min(2048 - bytes_recd, 2048))
                    if chunk == b'':
                        raise RuntimeError("socket connection broken")
                    chunks.append(chunk)
                    bytes_recd = bytes_recd + len(chunk)
                return b''.join(chunks)
            

            data = myreceive()


            if data == b'':
                print("Producer disconnected?")
                break
            
            try:
                ring_buffer.try_write(data)
                print(f'producer index {ring_buffer.writer.position.index} generation {ring_buffer.writer.position.generation}')
            except ringbuffer.WaitingForReaderError:
                ring_buffer.force_reader_sync()
                print("were syncing, were syncing")

        #ring_buffer.writer_done()
        #mountpoint_db.remove(mountpoint)


    def consumer_flow(self, http_request_line_list, mountpoint):

        if mountpoint in mountpoint_db:

            try:

                self.request.sendall(b"HTTP/1.1 200 OK\r\n")
                self.request.sendall(b"Content-Type: audio/mp3\r\n")
                # self.request.sendall(b"Content-Disposition: inline\r\n")
                # self.request.sendall(b"Ice-Audio-Info: ice-samplerate=48000;ice-bitrate=320;ice-channels=2\r\n")
                # self.request.sendall(b"Ice-Bitrate: 320\r\n")
                # self.request.sendall(b"Connection: keep-alive\r\n")
                # self.request.sendall(b"Access-Control-Allow-Origin: *\r\n")
                # self.request.sendall(b"Cache-Control: no-cache, no-store\r\n")
                self.request.sendall(b"\r\n")
                
                ring_buffer : ringbuffer.RingBuffer = mountpoint_db[mountpoint]['ringbuffer']
                pointer = ring_buffer.new_reader()

                while True:
                    try :
                        data = ring_buffer.blocking_read(pointer)
                    except ringbuffer.WaitingForWriterError:
                        print("WaitingForWriterError")
                        continue
                    print(f'consumer index {pointer.position.index} generation {pointer.position.generation}')
                    self.request.sendall(data)
            
            except Exception as e:
                print(repr(e))
                print("Removing reader")
                # This operation is very important as orphaned readers cause the whole stream 
                # to resync and glitch every time the writer wraps around to the dead reader.
                ring_buffer.readers.remove(pointer)
            
        else: # when mountpoint is not recognised
            return self.error_out()
            


    def handle(self):

        # New client has connected.
        print(f"New connection from {self.client_address}")

        # Read the first chunk of the request sent by the new client.
        time.sleep(0.1)
        recv_data : bytearray = self.request.recv(1024).strip()

        # Check if the data contains out magic values
        if (not recv_data[:3] == b'PUT') and (not recv_data[:3] == b'GET'):
            return self.error_out()
        
        # Convert http request to list of lines for parsing
        http_request = recv_data.decode('utf-8')
        #print(http_request)
        http_request_line_list = http_request.split('\n')

        # Detect parameters for streaming including action and mountpoint
        request_banner = http_request_line_list[0]          # PUT /song.mp3 HTTP/1.1 (or) GET /song.mp3 HTTP/1.1
        http_verb      = request_banner.split(" ")[0]       # PUT (or) GET
        mountpoint     = request_banner.split(" ")[1]       # /song.mp3

        if http_verb == "PUT":
            print("Connecting client wants to be producer")
            self.producer_flow(http_request_line_list, mountpoint)

        if http_verb == "GET":
            print("Connecting client wants to be consumer")
            self.consumer_flow(http_request_line_list, mountpoint)



def main():
    server = ThreadingTCPServer(("0.0.0.0", 80), ExtendedBaseRequestHandler)
    print("Starting server...")
    server.serve_forever()



if __name__ == "__main__":
    main()