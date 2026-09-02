from machine import Pin, SPI
from time import sleep_ms
import micropython

# Pin definitions for e-Paper display
BUSY_PIN = 13
RST_PIN = 12
DC_PIN = 14
CS_PIN = 27
SCK_PIN = 18
SDI_PIN = 23

# Global flag to switch between hardware and software SPI
USE_HARDWARE_SPI = True  # Set to False to use software SPI

# Display resolution constants
EPD_WIDTH = 400
EPD_HEIGHT = 300
EPD_WIDTH_BYTES = EPD_WIDTH // 8  # Width in bytes (400/8 = 50)

# Look-up table for 4-gray display mode
LUT_ALL = bytes([
0x01,	0x0A,	0x1B,	0x0F,	0x03,	0x01,	0x01,	
0x05,	0x0A,	0x01,	0x0A,	0x01,	0x01,	0x01,	
0x05,	0x08,	0x03,	0x02,	0x04,	0x01,	0x01,	
0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x0A,	0x1B,	0x0F,	0x03,	0x01,	0x01,	
0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
0x05,	0x48,	0x03,	0x82,	0x84,	0x01,	0x01,	
0x01,	0x84,	0x84,	0x82,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x0A,	0x1B,	0x8F,	0x03,	0x01,	0x01,	
0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
0x05,	0x48,	0x83,	0x82,	0x04,	0x01,	0x01,	
0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x8A,	0x1B,	0x8F,	0x03,	0x01,	0x01,	
0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
0x05,	0x48,	0x83,	0x02,	0x04,	0x01,	0x01,	
0x01,	0x04,	0x04,	0x02,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x8A,	0x9B,	0x8F,	0x03,	0x01,	0x01,	
0x05,	0x4A,	0x01,	0x8A,	0x01,	0x01,	0x01,	
0x05,	0x48,	0x03,	0x42,	0x04,	0x01,	0x01,	
0x01,	0x04,	0x04,	0x42,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x01,	0x00,	0x00,	0x00,	0x00,	0x01,	0x01,	
0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
0x02,	0x00,	0x00,	0x07,	0x17,	0x41,	0xA8,	
0x32,	0x30
])

class EPaper:
    def __init__(self):
        self.spi = None
        self.busy = None
        self.rst = None
        self.dc = None
        self.cs = None
        self.sck = None
        self.mosi = None
        self.setup_pins()

    def setup_pins(self):
        """Initialize all pins and SPI for the e-Paper display.
        This method sets up the pins for the display and initializes the SPI interface.
        It uses hardware SPI if USE_HARDWARE_SPI is set to True, otherwise it uses software SPI."""
        if USE_HARDWARE_SPI:
            self.spi = SPI(1, baudrate=4000000, polarity=0, phase=0, firstbit=SPI.MSB,
                          sck=Pin(SCK_PIN), mosi=Pin(SDI_PIN))
        else:
            self.spi = None
            self.sck = Pin(SCK_PIN, Pin.OUT)
            self.mosi = Pin(SDI_PIN, Pin.OUT)
        
        self.busy = Pin(BUSY_PIN, Pin.IN)      # Busy signal input
        self.rst = Pin(RST_PIN, Pin.OUT)       # Reset control
        self.dc = Pin(DC_PIN, Pin.OUT)         # Data/Command control
        self.cs = Pin(CS_PIN, Pin.OUT)         # Chip select
        
        self.cs.on()                           # Disable chip select
        self.dc.on()                           # Default to data mode
        self.rst.on()                          # No reset

    @micropython.native
    def spi_write_byte(self, data):
        """Write a single byte to the SPI bus.
        Args:
            data: The byte to be sent
        """
        if USE_HARDWARE_SPI:
            self.spi.write(bytes([data]))
        else:
            self.spi_send_byte_soft(data)

    @micropython.native
    def spi_write_bytes(self, data, length=None):
        """Write multiple bytes to the SPI bus."""
        if USE_HARDWARE_SPI:
            self.spi.write(data)
        else:
            if length is None:
                length = len(data)
            for i in range(length):
                self.spi_send_byte_soft(data[i])

    @micropython.native
    def spi_send_byte_soft(self, data):
        """Software SPI implementation to send a byte."""
        self.cs.off()  # Active low
        for i in range(8):
            if (data & 0x80):
                self.mosi.on()
            else:
                self.mosi.off()
            data <<= 1
            self.sck.on()
            self.sck.off()
        self.cs.on()

    @micropython.native
    def send_command(self, command):
        """Send command to the e-Paper display."""
        self.dc.off()  # Command mode (DC pin low)
        self.cs.off()  # Select device (CS pin low)
        self.spi_write_byte(command)
        self.cs.on()   # Deselect device (CS pin high)

    @micropython.native
    def send_data(self, data):
        """Send data to the e-Paper display."""
        self.dc.on()   # Data mode (DC pin high)
        self.cs.off()  # Select device (CS pin low)
        self.spi_write_byte(data)
        self.cs.on()   # Deselect device (CS pin high)

    @micropython.native
    def send_data_bytes(self, data, length=None):
        """Send multiple bytes of data to the e-Paper display."""
        self.dc.on()   # Data mode (DC pin high)
        self.cs.off()  # Select device (CS pin low)
        self.spi_write_bytes(data, length)
        self.cs.on()   # Deselect device (CS pin high)

    @micropython.native
    def read_busy(self):
        """Wait until the busy pin goes LOW (idle state)."""
        print("e-Paper busy")
        while self.busy.value() == 1:      # HIGH: busy, LOW: idle
            sleep_ms(10)
        print("e-Paper busy release")

    @micropython.native
    def reset(self):
        """Software reset for the e-Paper display."""
        self.rst.on()  # Set RST pin high
        sleep_ms(100)  # 100ms delay
        self.rst.off()  # Set RST pin low
        sleep_ms(2)  # 2ms delay
        self.rst.on()  # Set RST pin high
        sleep_ms(100)  # 100ms delay

    @micropython.native
    def turn_on_display(self):
        """Turn on the display with normal mode."""
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.read_busy()

    @micropython.native
    def turn_on_display_fast(self):
        """Turn on the display with fast mode."""
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.read_busy()

    @micropython.native
    def turn_on_display_partial(self):
        """Turn on the display for partial refresh."""
        self.send_command(0x22)
        self.send_data(0xFF)
        self.send_command(0x20)
        self.read_busy()

    @micropython.native
    def turn_on_display_4gray(self):
        """Turn on the display in 4 gray scale mode."""
        self.send_command(0x22)
        self.send_data(0xCF)
        self.send_command(0x20)
        self.read_busy()

    @micropython.native
    def set_window(self, x_start, y_start, width, height):
        """Set the display window area.
            width of area must be multiple of 8
        Args:
            x_start: Starting X coordinate (must be multiple of 8)
            y_start: Starting Y coordinate
            width: Width of the area in pixels (must be multiple of 8)
            height: Height of the area in pixels
        """
        if x_start % 8 != 0:
            raise ValueError("x_start must be a multiple of 8")
        if width % 8 != 0:
            raise ValueError("width must be a multiple of 8")
        
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data(((x_start + width -1) >> 3) & 0xFF)
        
        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        y_end = y_start + height - 1
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    @micropython.native
    def set_cursor(self, x_start, y_start):
        """Set the cursor position."""
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        self.send_data((x_start >> 3) & 0xFF)
        
        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)

    @micropython.native
    def load_4gray_lut(self):
        """Load the 4-gray Look-Up Table."""
        # WS byte 0~152
        self.send_command(0x32)
        for i in range(227):
            self.send_data(LUT_ALL[i])
        
        # WS byte 153 - Option for LUT end
        self.send_command(0x3F)
        self.send_data(LUT_ALL[227])
        
        # WS byte 154 - Gate level
        self.send_command(0x03)
        self.send_data(LUT_ALL[228])  # VGH
        
        # WS bytes 155~157 - Source level
        self.send_command(0x04)
        self.send_data(LUT_ALL[229])  # VSH1
        self.send_data(LUT_ALL[230])  # VSH2
        self.send_data(LUT_ALL[231])  # VSL
        
        # WS byte 158 - VCOM level
        self.send_command(0x2C)
        self.send_data(LUT_ALL[232])  # VCOM

    @micropython.native
    def init(self):
        """Initialize the e-Paper display."""
        self.reset()
        self.read_busy()
        self.send_command(0x12)   # soft reset
        self.read_busy()
        
        self.send_command(0x21)   # Display update control
        self.send_data(0x40)
        self.send_data(0x00)

        self.send_command(0x3C)   # BorderWavefrom
        self.send_data(0x05)
        
        self.send_command(0x11)   # data entry mode
        self.send_data(0x03)      # X-mode
        
        self.set_window(0, 0, EPD_WIDTH, EPD_HEIGHT)
        self.set_cursor(0, 0)
        self.read_busy()

    @micropython.native
    def init_4gray(self):
        """Initialize the display in 4-gray mode."""
        self.reset()
        
        self.send_command(0x12)   # soft reset
        self.read_busy()

        self.send_command(0x21)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)   # BorderWavefrom
        self.send_data(0x03)

        self.send_command(0x0C)   # BTST
        self.send_data(0x8B)
        self.send_data(0x9C)
        self.send_data(0xA4)
        self.send_data(0x0F)

        self.load_4gray_lut()     # Load 4-gray look-up table

        self.send_command(0x11)   # data entry mode
        self.send_data(0x03)      # X-mode
        
        self.set_window(0, 0, EPD_WIDTH, EPD_HEIGHT)
        self.set_cursor(0, 0)
        self.read_busy()

    @micropython.native
    def clear(self):
        """Clear the display screen to white."""
        line = bytearray(EPD_WIDTH_BYTES)
        for i in range(EPD_WIDTH_BYTES):
            line[i] = 0xFF

        self.send_command(0x24)
        for j in range(EPD_HEIGHT):
            self.send_data_bytes(line)

        self.send_command(0x26)
        for j in range(EPD_HEIGHT):
            self.send_data_bytes(line)
            
        self.turn_on_display()

    @micropython.native
    def display_4gray(self, gray, black):
        """Display a 4 gray levels image
        Args:
            black: most significant darkness
            gray: least significant darkness
        Levels are inverted :
        | gray | black | color      |
        | 0xFF | 0xFF  | white      |
        | 0x00 | 0xFF  | light gray |
        | 0xFF | 0x00  | dark gray  |
        | 0x00 | 0x00  | black      |
        """
        self.send_command(0x24)
        self.send_data_bytes(gray, EPD_WIDTH_BYTES * EPD_HEIGHT)

        self.send_command(0x26)
        self.send_data_bytes(black, EPD_WIDTH_BYTES * EPD_HEIGHT)
                
        self.turn_on_display_4gray()


    @micropython.native
    def display(self,black, fast=False): 
        """Display a black and white bitmap
        Args:
            black: bitmap to display
        Levels are inverted :
        | black | color      |
        | 0xFF  | white      |
        | 0x00  | black      |
        """
        self.send_command(0x24)
        self.send_data_bytes(black, EPD_WIDTH_BYTES * EPD_HEIGHT)

        self.send_command(0x26)
        self.send_data_bytes(black, EPD_WIDTH_BYTES * EPD_HEIGHT)

        if fast:
            self.turn_on_display_fast()
        else:        
            self.turn_on_display()

    @micropython.native
    def sleep(self):
        """Put display into deep sleep mode."""
        self.send_command(0x10)  # Deep sleep
        self.send_data(0x01)
        sleep_ms(200)

    @micropython.native
    def display_window(self, black, x_start, y_start, width, height):
        """Display a partial region of the screen
        Args:
            image: bitmap data to display
            x_start: starting X coordinate (must be multiple of 8)
            y_start: starting Y coordinate
            width: width of the area in pixels (must be multiple of 8)
            height: height of the area in pixels
        """
        # Enter partial mode
        self.send_command(0x21)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)
        self.send_data(0x80)

        # Set data entry mode
        self.send_command(0x11)
        self.send_data(0x03)  # X increment, Y increment
        
        # Set window
        self.set_window(x_start, y_start, width, height)

        # Set cursor
        self.set_cursor(x_start, y_start)

        self.read_busy()

        # Send black image data
        self.send_command(0x24)
        self.send_data_bytes(black)

        # Update display
        self.turn_on_display_partial()