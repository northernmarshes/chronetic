from epaper import EPaper, EPD_WIDTH_BYTES, EPD_HEIGHT
from draw_utils import print_text_scaled, load_raw_image
from time import sleep
import network
import machine
import secrets
# from dotenv import load_dotenv


def do_connect(ssid, key):
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(ssid, key)
        while not wlan.isconnected():
            machine.idle()
    print("network config:", wlan.ipconfig("addr4"))


def timetable(epd):
    print("init_4gray()")
    epd.init_4gray()
    # Create image buffers
    gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    # Initialize buffers to white
    for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
        gray[i] = 0xFF
        black[i] = 0xFF

    # load raw image
    load_raw_image(black, 0, 0, EPD_WIDTH_BYTES, "output_plane0.raw", 400, 300)

    # Display the image
    print("display_4gray()")

    # Print test text
    print_text_scaled("11:56", 2, 50, 2, gray, black, 0)
    print_text_scaled("12:05", 2, 80, 2, gray, black, 0)
    print_text_scaled("12:09", 2, 110, 2, gray, black, 0)
    print_text_scaled("12:13", 2, 140, 2, gray, black, 0)
    print_text_scaled("12:19", 2, 170, 2, gray, black, 0)
    print_text_scaled("12:25", 2, 200, 2, gray, black, 0)
    print_text_scaled("12:37", 2, 230, 2, gray, black, 0)

    # Buses
    print_text_scaled("123", 90, 50, 2, gray, black, 0)
    print_text_scaled("101", 90, 80, 2, gray, black, 0)
    print_text_scaled("143", 90, 110, 2, gray, black, 0)
    print_text_scaled("101", 90, 140, 2, gray, black, 0)
    print_text_scaled("143", 90, 170, 2, gray, black, 0)
    print_text_scaled("101", 90, 200, 2, gray, black, 0)
    print_text_scaled("123", 90, 230, 2, gray, black, 0)

    # Directions
    print_text_scaled("Dw. Wschodni", 170, 55, 1, gray, black, 0)
    print_text_scaled("Esperanto", 170, 85, 1, gray, black, 0)
    print_text_scaled("Dw. Glowny", 170, 115, 1, gray, black, 0)
    print_text_scaled("Esperanto", 170, 145, 1, gray, black, 0)
    print_text_scaled("Dw. Glowny", 170, 175, 1, gray, black, 0)
    print_text_scaled("Esperanto", 170, 205, 1, gray, black, 0)
    print_text_scaled("Dw. Wschodni", 170, 235, 1, gray, black, 0)

    # Stops
    print_text_scaled("Rondo K.", 320, 55, 1, gray, black, 0)
    print_text_scaled("Rondo K.", 320, 85, 1, gray, black, 0)
    print_text_scaled("Rondo K.", 320, 115, 1, gray, black, 0)
    print_text_scaled("Rondo K.", 320, 145, 1, gray, black, 0)
    print_text_scaled("Rondo K.", 320, 175, 1, gray, black, 0)
    print_text_scaled("Rondo K.", 320, 205, 1, gray, black, 0)
    print_text_scaled("Rondo K.", 320, 235, 1, gray, black, 0)

    # epd.display(black)
    epd.display_4gray(black, black)
    sleep(2)


if __name__ == "__main__":
    # load_dotenv()

    ssid = secrets.SSID
    key = secrets.KEY

    # Connect wifi
    do_connect(ssid, key)

    # Initialize display
    epd = EPaper()

    # black_and_white_demo(epd)
    timetable(epd)

    print("sleep()")
    epd.sleep()
