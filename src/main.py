from epaper import EPaper, EPD_WIDTH_BYTES, EPD_HEIGHT
from draw_utils import print_text_scaled, load_raw_image
from time import sleep
import requests
import time
import json
import ntptime
import network
import machine
import secrets

# Load eviormental variables
SSID = secrets.SSID
KEY = secrets.KEY
API_URL = secrets.API_URL
API_KEY = secrets.API_KEY
LIST_ID = secrets.LIST_ID
STOP_ID = secrets.STOP_ID
TIMETABLE_ID = secrets.TIMETABLE_ID
TEST_URL = secrets.TEST_URL
STOP_NR = secrets.STOP_NR


BUS_STOP_URL = (
    API_URL
    + "/?id="
    + LIST_ID
    + "&busstopId="
    + STOP_ID
    + "&busstopNr="
    + STOP_NR
    + "&apikey="
    + API_KEY
)


def main():
    pass


def construct_timetable(bus: str) -> list:
    """Make a sorted list of all departures"""
    departures: list = []
    tt_url: str = make_tt_url(bus)
    r = requests.get(tt_url)
    if r:
        print("timetable fetched!")
    data = json.loads(json.dumps(r.json()))

    # Create one departure
    departures: list = []

    for result in data["result"]:
        single_departure: list = []
        time = str(result[5]["value"])[:-3]
        hours = int(time[:-3])
        minutes = int(time[-2:])
        if hours > 24:
            true_hours = hours - 24
            true_hours = "{:02d}".format(true_hours)
            time = str(true_hours) + ":" + str(minutes)
        single_departure.append(time)
        single_departure.append(bus)
        single_departure.append(result[3]["value"])
        single_departure.append("Rondo K.")
        departures.append(single_departure)

    return departures


def make_tt_url(line) -> str:
    "Construct url for each line"
    url = (
        API_URL
        + "/?apikey="
        + API_KEY
        + "&id="
        # tu się sypie
        + TIMETABLE_ID
        + "&busstopId="
        + STOP_ID
        + "&busstopNr="
        + STOP_NR
        + "&line="
        + line
    )
    return url


def do_connect(ssid, key):
    """Connect to the WIFI"""
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(ssid, key)
        while not wlan.isconnected():
            machine.idle()
    print("network config:", wlan.ipconfig("addr4"))


def get_buses(url) -> list:
    """Get buses list for a bus stop"""
    buses_list = []
    r = requests.get(url)
    data = json.dumps(r.json())
    data = json.loads(data)
    for result in data["result"]:
        bus = str([item["value"] for item in result["values"]])
        buses_list.append(bus[2:-2])
    return buses_list


def fetch_test(url) -> str:
    """Test the connection"""
    print("Fetching test data...")
    test_response = str((requests.get(url)).content)
    if test_response:
        print("Data fetched!")
        print("Response:", test_response)
    else:
        print("Didn't fetch :(")
    return test_response


def draw_error():
    # Initialize epd
    print("init_4gray()")
    epd.init_4gray()
    # Create image buffers
    gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    # Initialize buffers to white
    for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
        gray[i] = 0xFF
        black[i] = 0xFF

    # Load raw image
    # load_raw_image(black, 0, 0, EPD_WIDTH_BYTES, "output_plane0.raw", 400, 300)

    print_text_scaled("ERROR", 150, 145, 3, gray, black, 0)

    # epd.display(black)
    epd.display_4gray(black, black)
    sleep(2)


def draw_timetable(epd, test, now, date):
    # Initialize epd
    print("init_4gray()")
    epd.init_4gray()
    # Create image buffers
    gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    # Initialize buffers to white
    for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
        gray[i] = 0xFF
        black[i] = 0xFF

    # Load raw image
    load_raw_image(black, 0, 0, EPD_WIDTH_BYTES, "output_plane0.raw", 400, 300)

    # Drawing data
    print("Drawing data...")

    # Departure times
    print_text_scaled(test[0][0], 2, 50, 2, gray, black, 0)
    print_text_scaled(test[1][0], 2, 80, 2, gray, black, 0)
    print_text_scaled(test[2][0], 2, 110, 2, gray, black, 0)
    print_text_scaled(test[3][0], 2, 140, 2, gray, black, 0)
    print_text_scaled(test[4][0], 2, 170, 2, gray, black, 0)
    print_text_scaled(test[5][0], 2, 200, 2, gray, black, 0)
    print_text_scaled(test[0][0], 2, 230, 2, gray, black, 0)

    # Buses
    print_text_scaled(test[0][1], 90, 50, 2, gray, black, 0)
    print_text_scaled(test[1][1], 90, 80, 2, gray, black, 0)
    print_text_scaled(test[2][1], 90, 110, 2, gray, black, 0)
    print_text_scaled(test[3][1], 90, 140, 2, gray, black, 0)
    print_text_scaled(test[4][1], 90, 170, 2, gray, black, 0)
    print_text_scaled(test[5][1], 90, 200, 2, gray, black, 0)
    print_text_scaled(test[0][1], 90, 230, 2, gray, black, 0)

    # Directions
    print_text_scaled(test[0][2], 170, 55, 1, gray, black, 0)
    print_text_scaled(test[1][2], 170, 85, 1, gray, black, 0)
    print_text_scaled(test[2][2], 170, 115, 1, gray, black, 0)
    print_text_scaled(test[3][2], 170, 145, 1, gray, black, 0)
    print_text_scaled(test[4][2], 170, 175, 1, gray, black, 0)
    print_text_scaled(test[5][2], 170, 205, 1, gray, black, 0)
    print_text_scaled(test[0][2], 170, 235, 1, gray, black, 0)

    # Stops
    print_text_scaled(test[0][3], 320, 55, 1, gray, black, 0)
    print_text_scaled(test[1][3], 320, 85, 1, gray, black, 0)
    print_text_scaled(test[2][3], 320, 115, 1, gray, black, 0)
    print_text_scaled(test[3][3], 320, 145, 1, gray, black, 0)
    print_text_scaled(test[4][3], 320, 175, 1, gray, black, 0)
    print_text_scaled(test[5][3], 320, 205, 1, gray, black, 0)
    print_text_scaled(test[0][3], 320, 235, 1, gray, black, 0)

    # Time
    print_text_scaled(now, 310, 274, 2, gray, black, 0)
    print_text_scaled(date, 7, 274, 2, gray, black, 0)

    # epd.display(black)
    epd.display_4gray(black, black)
    sleep(2)


if __name__ == "__main__":
    # Connect wifi and get data
    do_connect(SSID, KEY)

    # Get current time
    ntptime.settime()
    timestamp = time.localtime()
    utc = 2
    now = str(timestamp[3] + utc) + ":" + str(timestamp[4])
    date = str(timestamp[0]) + "-" + str(timestamp[1]) + "-" + str(timestamp[2])
    print("date:", date)
    print("time:", now)

    # Get buses list
    buses_list = get_buses(BUS_STOP_URL)
    first_bus = str(buses_list[0])

    # Get timetables
    departures = construct_timetable(buses_list[0])

    for departure in departures:
        print(departure)

    # Initialize display
    epd = EPaper()

    # Display UI
    draw_timetable(epd, departures, now, date)

    # Display error
    # draw_error()

    print("sleep()")
    epd.sleep()
