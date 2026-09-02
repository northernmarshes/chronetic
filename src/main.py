from epaper import EPaper, EPD_WIDTH_BYTES, EPD_HEIGHT
from draw_utils import draw_line, print_text_scaled, draw_frame, load_raw_image
from time import sleep


def black_and_white_demo(epd):
    print("init()")
    epd.init()
    print("clear()")
    epd.clear()

    # Create image buffers
    gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)

    # Initialize buffers to white
    for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
        gray[i] = 0xFF
        black[i] = 0xFF

    # Draw frame and test pattern
    black = draw_frame(black)
    for y in range(0, EPD_HEIGHT):
        # 0x00 0x00 -> black
        gray[y * EPD_WIDTH_BYTES] = 0x00
        black[y * EPD_WIDTH_BYTES] = 0x00
        # 0x00 0xFF -> dark gray
        gray[y * EPD_WIDTH_BYTES + 1] = 0xFF
        black[y * EPD_WIDTH_BYTES + 1] = 0x00
        # 0xFF 0x00 -> light gray
        gray[y * EPD_WIDTH_BYTES + 2] = 0x00
        black[y * EPD_WIDTH_BYTES + 2] = 0xFF

    # Draw diagonal line
    draw_line(0, 0, 399, 299, gray, black, color=0)  # Draw black line

    # Print test text
    print_text_scaled("BLACK and WHITE demo", 16, 64, 2, gray, black, 0)

    # Display the image
    print("display()")
    epd.display(black, True)
    # Partial update
    print("partial_display()")
    width = 64
    height = 48
    bytes_width = width // 8
    partial = bytearray(height * bytes_width)
    for y in range(0, height):
        for x in range(0, bytes_width):
            if y % 8 < 4:
                partial[x + y * bytes_width] = 0x0F
            else:
                partial[x + y * bytes_width] = 0xF0

    print("partial display")
    epd.display_window(partial, 0, 0, width, height)
    sleep(1)
    epd.display_window(partial, 64, 48, width, height)
    sleep(1)
    sleep(3)


def four_gray_demo(epd):
    print("init_4gray()")
    epd.init_4gray()
    # Create image buffers
    gray = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    black = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
    # Initialize buffers to white
    for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
        gray[i] = 0xFF
        black[i] = 0xFF

    # Draw frame and test pattern
    # black = draw_frame(black)
    # for y in range(0, EPD_HEIGHT):
    #     # 0x00 0x00 -> black
    #     gray[y * EPD_WIDTH_BYTES] = 0x00
    #     black[y * EPD_WIDTH_BYTES] = 0x00
    #     # 0x00 0xFF -> dark gray
    #     gray[y * EPD_WIDTH_BYTES + 1] = 0xFF
    #     black[y * EPD_WIDTH_BYTES + 1] = 0x00
    #     # 0xFF 0x00 -> light gray
    #     gray[y * EPD_WIDTH_BYTES + 2] = 0x00
    #     black[y * EPD_WIDTH_BYTES + 2] = 0xFF
    # Draw diagonal line
    # draw_line(0, 0, 399, 299, gray, black, color=1)  # Draw gray line

    # load raw image
    # load_raw_image(gray, 100, 140, EPD_WIDTH_BYTES, "output_plane0.raw", 200, 113)
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
    # Initialize display
    epd = EPaper()

    # black_and_white_demo(epd)
    four_gray_demo(epd)

    print("sleep()")
    epd.sleep()
