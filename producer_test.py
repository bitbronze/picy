import base64, socket, time

all_headers = {
    "ice-public"        : "value", # For a mountpoint that doesn't has <public> configured, this influences if the mountpoint shoult be advertised to a YP directory or not. Value can either be 0 (not public) or 1 (public).
    "ice-name"          : "value", # For a mountpoint that doesn't has <stream-name> configured, this sets the name of the stream.
    "ice-description"   : "value", # For a mountpoint that doesn't has <stream-description> configured, this sets the description of the stream.
    "ice-url"           : "value", # For a mountpoint that doesn't has <stream-url> configure, this sets the URL to the Website of the stream. (This should _not_ be the Server or mountpoint URL)
    "ice-genre"         : "value", # For a mountpoint that doesn't has <genre> configure, this sets the genre of the stream.
    "ice-bitrate"       : "value", # This sets the bitrate of the stream.
    "ice-audio-info"    : "value", # A Key-Value list of audio information about the stream, using = as separator between key and value and ; as separator of the Key-Value pairs. Values must be URL-encoded if necessary. Example: samplerate=44100;quality=10%2e0;channels=2
    "Content-Type"      : "value", # Indicates the content type of the stream, this must be set.
    "Expect"            : "100-continue"
}

custom_headers = {
    "ice-public"        : "value",
    "ice-name"          : "This is the name of the stream e.g. Cool Radio UK",
    "ice-description"   : "We play cool music only. We are based in the UK.",
    "ice-genre"         : "Pop",
    "Content-Type"      : "audio/mp3",
    "Expect"            : "100-continue"
}





target_host = '127.0.0.1'
target_port = 80
mountpoint = '/song.mp3'


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    
    sock.setblocking(False)
    sock.settimeout(1)

    sock.connect((target_host, target_port))

    sock.sendall(b'PUT /song.mp3 HTTP/1.1\n')
    sock.sendall(b'Host: 127.0.0.1:80\n')
    sock.sendall(b'Authorization: Basic YWRtaW46cGFzcw==\n')
    sock.sendall(b'User-Agent: picy-test-stream-producer\n')

    for header in custom_headers:
        sock.sendall(bytes(f'{header}: {custom_headers[header]}\n', 'utf-8'))

    initial_response = sock.recv(1024)

print('Received', repr(initial_response))



