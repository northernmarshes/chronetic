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

# Conctruct urls
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
    app = Chronetic()
    app.run()


class Chronetic(EPaper):
    def __init__(self):
        super().__init__()

        # Connect wifi and get data
        self.do_connect()

        # Get current time
        ntptime.settime()
        timestamp = time.localtime()
        utc = 2

        self.current_hours = "{:02d}".format(timestamp[3] + utc)
        self.current_minutes = "{:02d}".format(timestamp[4])
        self.now = str(self.current_hours) + ":" + str(self.current_minutes)

        self.date = (
            str(timestamp[0]) + "-" + str(timestamp[1]) + "-" + str(timestamp[2])
        )
        print("date:", self.date)
        print("time:", self.now)

    def run(self):
        # Get buses list
        buses_list = self.get_buses()
        self.first_bus = str(buses_list[0])

        # Get timetables
        self.test = self.construct_timetable()

        # for departure in departures:
        #     print(departure)

        # Initialize display
        self.epd = EPaper()

        # Display UI
        self.draw_timetable()

        # Display error
        # draw_error()

        print("sleep()")
        self.epd.sleep()

    def construct_timetable(self) -> list:
        """Make a sorted list of all departures"""
        departures: list = []
        tt_url: str = self.make_tt_url()
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
                true_minutes = "{:02d}".format(minutes)
                time = str(true_hours) + ":" + str(true_minutes)
            single_departure.append(time)
            single_departure.append(self.first_bus)
            single_departure.append(result[3]["value"])
            single_departure.append("Rondo K.")
            departures.append(single_departure)

        return departures

    def make_tt_url(self) -> str:
        "Construct url for each line"
        self.test_url = (
            API_URL
            + "/?apikey="
            + API_KEY
            + "&id="
            + TIMETABLE_ID
            + "&busstopId="
            + STOP_ID
            + "&busstopNr="
            + STOP_NR
            + "&line="
            + self.first_bus
        )
        return self.test_url

    def do_connect(self):
        """Connect to the WIFI"""
        wlan = network.WLAN()
        wlan.active(True)
        if not wlan.isconnected():
            print("connecting to network...")
            wlan.connect(SSID, KEY)
            while not wlan.isconnected():
                machine.idle()
        print("network config:", wlan.ipconfig("addr4"))

    def get_buses(self) -> list:
        """Get buses list for a bus stop"""
        buses_list = []
        r = requests.get(BUS_STOP_URL)
        data = json.dumps(r.json())
        data = json.loads(data)
        for result in data["result"]:
            bus = str([item["value"] for item in result["values"]])
            buses_list.append(bus[2:-2])
        return buses_list

    def fetch_test(self) -> str:
        """Test the connection"""
        print("Fetching test data...")
        test_response = str((requests.get(TEST_URL)).content)
        if test_response:
            print("Data fetched!")
            print("Response:", test_response)
        else:
            print("Didn't fetch :(")
        return test_response

    def draw_error(self):
        # Initialize epd
        print("init_4gray()")
        self.epd.init_4gray()
        # Create image buffers
        gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
        black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
        # Initialize buffers to white
        for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
            gray[i] = 0xFF
            black[i] = 0xFF

        print_text_scaled("ERROR", 150, 145, 3, gray, black, 0)

        # epd.display(black)
        self.epd.display_4gray(black, black)
        sleep(2)

    def draw_timetable(self):
        # Initialize epd
        print("init_4gray()")
        self.epd.init_4gray()
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
        print_text_scaled(self.test[0][0], 2, 50, 2, gray, black, 0)
        print_text_scaled(self.test[1][0], 2, 80, 2, gray, black, 0)
        print_text_scaled(self.test[2][0], 2, 110, 2, gray, black, 0)
        print_text_scaled(self.test[3][0], 2, 140, 2, gray, black, 0)
        print_text_scaled(self.test[4][0], 2, 170, 2, gray, black, 0)
        print_text_scaled(self.test[5][0], 2, 200, 2, gray, black, 0)
        print_text_scaled(self.test[0][0], 2, 230, 2, gray, black, 0)

        # Buses
        print_text_scaled(self.test[0][1], 90, 50, 2, gray, black, 0)
        print_text_scaled(self.test[1][1], 90, 80, 2, gray, black, 0)
        print_text_scaled(self.test[2][1], 90, 110, 2, gray, black, 0)
        print_text_scaled(self.test[3][1], 90, 140, 2, gray, black, 0)
        print_text_scaled(self.test[4][1], 90, 170, 2, gray, black, 0)
        print_text_scaled(self.test[5][1], 90, 200, 2, gray, black, 0)
        print_text_scaled(self.test[0][1], 90, 230, 2, gray, black, 0)

        # Directions
        print_text_scaled(self.test[0][2], 170, 55, 1, gray, black, 0)
        print_text_scaled(self.test[1][2], 170, 85, 1, gray, black, 0)
        print_text_scaled(self.test[2][2], 170, 115, 1, gray, black, 0)
        print_text_scaled(self.test[3][2], 170, 145, 1, gray, black, 0)
        print_text_scaled(self.test[4][2], 170, 175, 1, gray, black, 0)
        print_text_scaled(self.test[5][2], 170, 205, 1, gray, black, 0)
        print_text_scaled(self.test[0][2], 170, 235, 1, gray, black, 0)

        # Stops
        print_text_scaled(self.test[0][3], 320, 55, 1, gray, black, 0)
        print_text_scaled(self.test[1][3], 320, 85, 1, gray, black, 0)
        print_text_scaled(self.test[2][3], 320, 115, 1, gray, black, 0)
        print_text_scaled(self.test[3][3], 320, 145, 1, gray, black, 0)
        print_text_scaled(self.test[4][3], 320, 175, 1, gray, black, 0)
        print_text_scaled(self.test[5][3], 320, 205, 1, gray, black, 0)
        print_text_scaled(self.test[0][3], 320, 235, 1, gray, black, 0)

        # Time
        print_text_scaled(self.now, 310, 274, 2, gray, black, 0)
        print_text_scaled(self.date, 7, 274, 2, gray, black, 0)

        # epd.display(black)
        self.epd.display_4gray(black, black)
        sleep(2)


if __name__ == "__main__":
    main()
