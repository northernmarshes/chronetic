from epaper import EPaper, EPD_WIDTH_BYTES, EPD_HEIGHT
from draw_utils import draw_line, print_text, print_text_scaled, draw_frame
from time import sleep


def timetable(epd):
    pass


if __name__ == "__main__":
    # Initialize display
    epd = EPaper()

    # Draw timetable
    timetable(epd)

    epd.sleep()
