import requests

all_headers = {
    "ice-public"        : "value", # For a mountpoint that doesn't has <public> configured, this influences if the mountpoint shoult be advertised to a YP directory or not. Value can either be 0 (not public) or 1 (public).
    "ice-name"          : "value", # For a mountpoint that doesn't has <stream-name> configured, this sets the name of the stream.
    "ice-description"   : "value", # For a mountpoint that doesn't has <stream-description> configured, this sets the description of the stream.
    "ice-url"           : "value", # For a mountpoint that doesn't has <stream-url> configure, this sets the URL to the Website of the stream. (This should _not_ be the Server or mountpoint URL)
    "ice-genre"         : "value", # For a mountpoint that doesn't has <genre> configure, this sets the genre of the stream.
    "ice-bitrate"       : "value", # This sets the bitrate of the stream.
    "ice-audio-info"    : "value", # A Key-Value list of audio information about the stream, using = as separator between key and value and ; as separator of the Key-Value pairs. Values must be URL-encoded if necessary. Example: samplerate=44100;quality=10%2e0;channels=2
    "Content-Type"      : "value", # Indicates the content type of the stream, this must be set.
}

custom_headers = {
    "ice-public"        : "value",
    "ice-name"          : "value",
    "ice-description"   : "value",
    "ice-url"           : "value",
    "ice-genre"         : "value",
    "ice-bitrate"       : "value",
    "ice-audio-info"    : "value",
    "Content-Type"      : "value",
}

resp = requests.request(method="PUT", url="http://127.0.0.1/mp1/mp2/mp3", auth=("admin","pass"), headers=custom_headers)

print(resp.reason)
