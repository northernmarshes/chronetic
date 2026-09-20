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
URI = secrets.URI


def main():
    app = Chronetic()
    while 1:
        app.run()
        time.sleep(30)


class Chronetic(EPaper):
    def __init__(self):
        super().__init__()

        # Connect wifi and get data
        self.connect_wifi()
        time.sleep(30)

        # Get current time
        ntptime.settime()
        sleep(10)

    def run(self):
        # timestamp = time.localtime()
        local_time = time.localtime()
        timestamp = time.localtime(time.mktime(local_time) + (2 * 3600))
        # print("timestamp now is:", timestamp)
        today = timestamp[2]

        self.current_hours = "{:02d}".format(timestamp[3])
        # print("current_hours is:", self.current_hours)
        self.current_minutes = "{:02d}".format(timestamp[4])
        self.now = str(self.current_hours) + ":" + str(self.current_minutes)
        self.departures = []

        self.date = str(timestamp[0]) + "-" + str(timestamp[1]) + "-" + str(today)
        # print("self.date is: ", self.date)
        # print("date:", self.date)
        # print("time:", self.now)

        # Initialize display
        self.epd = EPaper()

        self.get_data()

        # Display UI
        self.draw_timetable()

        print("sleep()")
        self.epd.sleep()

    def get_data(self):
        """Fetch json and parse to list"""
        self.test: list = []
        r = None
        while r is None:
            try:
                r = requests.get(URI)
            except:
                pass
        # time.sleep(20)
        dump = json.dumps(r.json())
        data = json.loads(dump)
        count = 0
        for result in data["result"]:
            if count < 7:
                single_departure: list = []
                time_now = str(result[0]["value"])[:-3]
                hours = int(time_now[:-3])
                minutes = int(time_now[-2:])
                if hours >= 24:
                    true_hours = hours - 24
                    true_hours = "{:02d}".format(true_hours)
                    true_minutes = "{:02d}".format(minutes)
                    time_now = str(true_hours) + ":" + str(true_minutes)
                mam = int(time_now[:2]) * 60 + int(time_now[-2:])
                single_departure.append(time_now)
                single_departure.append(result[1]["value"])
                destination = result[2]["value"]
                destination = " ".join(destination.split()[:2])
                single_departure.append(destination)
                single_departure.append(result[3]["value"])
                single_departure.append(mam)
                self.test.append(single_departure)
                count += 1

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
        print_text_scaled(self.test[6][0], 2, 230, 2, gray, black, 0)

        # Buses
        print_text_scaled(self.test[0][1], 90, 50, 2, gray, black, 0)
        print_text_scaled(self.test[1][1], 90, 80, 2, gray, black, 0)
        print_text_scaled(self.test[2][1], 90, 110, 2, gray, black, 0)
        print_text_scaled(self.test[3][1], 90, 140, 2, gray, black, 0)
        print_text_scaled(self.test[4][1], 90, 170, 2, gray, black, 0)
        print_text_scaled(self.test[5][1], 90, 200, 2, gray, black, 0)
        print_text_scaled(self.test[6][1], 90, 230, 2, gray, black, 0)

        # Directions
        print_text_scaled(self.test[0][2], 170, 55, 1, gray, black, 0)
        print_text_scaled(self.test[1][2], 170, 85, 1, gray, black, 0)
        print_text_scaled(self.test[2][2], 170, 115, 1, gray, black, 0)
        print_text_scaled(self.test[3][2], 170, 145, 1, gray, black, 0)
        print_text_scaled(self.test[4][2], 170, 175, 1, gray, black, 0)
        print_text_scaled(self.test[5][2], 170, 205, 1, gray, black, 0)
        print_text_scaled(self.test[6][2], 170, 235, 1, gray, black, 0)

        # Stops
        print_text_scaled(self.test[0][3], 320, 55, 2, gray, black, 0)
        print_text_scaled(self.test[1][3], 320, 85, 2, gray, black, 0)
        print_text_scaled(self.test[2][3], 320, 115, 2, gray, black, 0)
        print_text_scaled(self.test[3][3], 320, 145, 2, gray, black, 0)
        print_text_scaled(self.test[4][3], 320, 175, 2, gray, black, 0)
        print_text_scaled(self.test[5][3], 320, 205, 2, gray, black, 0)
        print_text_scaled(self.test[6][3], 320, 235, 2, gray, black, 0)

        # Min
        print_text_scaled("min", 360, 60, 1, gray, black, 0)
        print_text_scaled("min", 360, 90, 1, gray, black, 0)
        print_text_scaled("min", 360, 120, 1, gray, black, 0)
        print_text_scaled("min", 360, 150, 1, gray, black, 0)
        print_text_scaled("min", 360, 180, 1, gray, black, 0)
        print_text_scaled("min", 360, 210, 1, gray, black, 0)
        print_text_scaled("min", 360, 240, 1, gray, black, 0)

        # Time
        print_text_scaled(self.now, 310, 274, 2, gray, black, 0)
        print_text_scaled(self.date, 7, 274, 2, gray, black, 0)

        # epd.display(black)
        self.epd.display_4gray(black, black)
        sleep(2)

    def connect_wifi(self):
        """Connect to the WIFI"""
        wlan = network.WLAN()
        wlan.active(True)
        if not wlan.isconnected():
            print("connecting to network...")
            wlan.connect(SSID, KEY)
            while not wlan.isconnected():
                machine.idle()
        print("network config:", wlan.ipconfig("addr4"))

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

    # def draw_word(self, word):
    #     # Initialize epd
    #     print("init_4gray()")
    #     self.epd.init_4gray()
    #     # Create image buffers
    #     gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    #     black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    #     # Initialize buffers to white
    #     for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
    #         gray[i] = 0xFF
    #         black[i] = 0xFF
    #     print_text_scaled(word, 150, 145, 3, gray, black, 0)
    #
    #     # epd.display(black)
    #     self.epd.display_4gray(black, black)
    #     sleep(2)


if __name__ == "__main__":
    main()
