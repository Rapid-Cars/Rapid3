import time
# noinspection PyUnresolvedReferences
import sensor
# noinspection PyUnresolvedReferences
import network
import socket
# noinspection PyUnresolvedReferences
import machine

# noinspection PyUnresolvedReferences
clock = time.clock()

# Setup Wi-Fi variables
# Use 192.168.4.1:8080 to connect
SSID = "OPENMV_AP"  # Network SSID
KEY = "1234567890"  # Network key (must be 10 chars)
HOST = ""
PORT = 8080
SOCKET = None
server = None

def setup_access_point():
    """
    Set up an access point with a given SSID, key, and channel, then activate it.

    This function configures and activates the WLAN interface in access point (AP)
    mode, applying the specified SSID, password key, and channel. After activation,
    it prints the SSID and the IP address of the access point to confirm that the
    AP mode was set up successfully.

    Returns:
        None
    """
    network.country('DE')
    wlan = network.WLAN(network.AP_IF)
    wlan.config(ssid=SSID, key=KEY, channel=2)
    wlan.active(True)
    print("AP mode started. SSID: {} IP: {}".format(SSID, wlan.ifconfig()[0]))


def stream_video(wifi_client):
    """
    Function to stream video data to a client via HTTP connection using a multipart/x-mixed-replace
    content type, suitable for streaming camera feeds.

    Parameters:
    client: Object used to handle client-specific operations. Must define methods such
             as 'recv' for receiving data and 'send' for sending HTTP responses.

    Raises:
    None
    """
    # Read request from client
    _ = wifi_client.recv(1024)
    # Should parse client request here

    # Send multipart header
    wifi_client.send(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    while True:
        main_loop(wifi_client)


setup_access_point()


def main_loop(_wifi_client):
    clock.tick()
    img = sensor.snapshot()  # Capture an image

    # You can process the image here


    cframe = img.to_jpeg(quality=35, copy=True)
    header = (
            "\r\n--openmv\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
    )
    _wifi_client.sendall(header)
    _wifi_client.sendall(cframe)

    print(clock.fps())


while True:
    if server is None:
        # Create server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # Bind and listen
        server.bind([HOST, PORT])
        server.listen(5)
        # Set server socket to blocking
        server.setblocking(True)

    try:
        print("Waiting for connections..")
        client, addr = server.accept()
    except OSError as e:
        server.close()
        server = None
        print("server socket error:", e)
        continue

    try:
        # set client socket timeout to 5s
        client.settimeout(5.0)
        print("Connected to " + addr[0] + ":" + str(addr[1]))
        stream_video(client)
    except OSError as e:
        client.close()
        print("client socket error:", e)
        # sys.print_exception(e)