import micropython
from micropython import const
from epaper import EPaper, EPD_WIDTH_BYTES, EPD_HEIGHT
from font8x8 import FONT8X8

# Constants
CHAR_WIDTH = const(8)
CHAR_HEIGHT = const(8)
PIXELS_PER_BYTE = const(8)

@micropython.native
def draw_line(x1, y1, x2, y2, gray_buffer, black_buffer, color=0):
    """Draw a single line using Bresenham's algorithm
    Args:
        x1: Starting X position in pixels
        y1: Starting Y position in pixels
        x2: Ending X position in pixels
        y2: Ending Y position in pixels
        gray_buffer: Buffer for gray bits
        black_buffer: Buffer for black bits
        color: Color value (0=black, 1=dark gray, 2=light gray, 3=white)
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while True:
        # Plot point (x1, y1)
        byte_pos = (x1 // 8) + (y1 * EPD_WIDTH_BYTES)
        bit_pos = 7 - (x1 % 8)
        
        if color in (0, 1):
            gray_buffer[byte_pos] &= ~(1 << bit_pos)
        if color in (0, 2):
            black_buffer[byte_pos] &= ~(1 << bit_pos)
            
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

@micropython.native
def print_char(char, x, y, gray_buffer, black_buffer, color=0):
    """Print a single character on the e-paper display.
    Args:
        char: Character to print (single ASCII character)
        x: X position in pixels
        y: Y position in pixels
        gray_buffer: Buffer for gray bits
        black_buffer: Buffer for black bits
        color: Color value (0=black, 1=dark gray, 2=light gray, 3=white)
    """
    if not 0 <= x < EPD_WIDTH_BYTES * PIXELS_PER_BYTE or not 0 <= y < EPD_HEIGHT:
        return
        
    # Get character bitmap from font
    char_idx = ord(char) - 0x20  # Adjust index since font starts at space (0x20)
    if char_idx < 0 or char_idx >= len(FONT8X8):
        return
    char_bitmap = FONT8X8[char_idx]
    
    # Calculate buffer positions
    byte_x = x // PIXELS_PER_BYTE
    bit_x = x % PIXELS_PER_BYTE
    
    # Set color bits according to grayscale value
    gray_bit = 1 if color in (0, 1) else 0  
    black_bit = 1 if color in (0, 2) else 0
    
    # Draw character bitmap
    for cy in range(CHAR_HEIGHT):
        if y + cy >= EPD_HEIGHT:
            break
            
        row = char_bitmap[cy]
        for cx in range(CHAR_WIDTH):
            if x + cx >= EPD_WIDTH_BYTES * PIXELS_PER_BYTE:
                break
                
            # Changed this line to read bits from left to right
            if row & (1 << cx):
                # Calculate byte position and bit mask
                curr_byte_x = (x + cx) // PIXELS_PER_BYTE
                curr_bit_x = (x + cx) % PIXELS_PER_BYTE
                mask = 0xFF ^ (1 << (7 - curr_bit_x))
                
                # Set bits according to color
                gray_byte = gray_buffer[curr_byte_x + (y + cy) * EPD_WIDTH_BYTES]
                black_byte = black_buffer[curr_byte_x + (y + cy) * EPD_WIDTH_BYTES]
                
                if gray_bit:
                    gray_byte &= mask
                else:
                    gray_byte |= (1 << (7 - curr_bit_x))
                    
                if black_bit:
                    black_byte &= mask
                else:
                    black_byte |= (1 << (7 - curr_bit_x))
                    
                gray_buffer[curr_byte_x + (y + cy) * EPD_WIDTH_BYTES] = gray_byte
                black_buffer[curr_byte_x + (y + cy) * EPD_WIDTH_BYTES] = black_byte

@micropython.native
def print_text(text, x, y, gray_buffer, black_buffer, color=0):
    """Print text string on the display.
    Args:
        text: String to print
        x: Starting X position in pixels
        y: Starting Y position in pixels
        gray_buffer: Buffer for gray bits
        black_buffer: Buffer for black bits
        color: Color value (0=black, 1=dark gray, 2=light gray, 3=white)
    """
    cursor_x = x
    for char in text:
        print_char(char, cursor_x, y, gray_buffer, black_buffer, color)
        cursor_x += CHAR_WIDTH

@micropython.native
def print_char_scaled(char, x, y, scale, gray_buffer, black_buffer, color=0):
    """Print a scaled character"""
    char_idx = ord(char) - 0x20
    if char_idx < 0 or char_idx >= len(FONT8X8):
        return
        
    char_bitmap = FONT8X8[char_idx]
    
    for cy in range(CHAR_HEIGHT):
        for sy in range(scale):  # Scale vertically
            if y + (cy * scale) + sy >= EPD_HEIGHT:
                break
                
            row = char_bitmap[cy]
            for cx in range(CHAR_WIDTH):
                for sx in range(scale):  # Scale horizontally
                    if x + (cx * scale) + sx >= EPD_WIDTH_BYTES * 8:
                        break
                        
                    if row & (1 << cx):
                        px = x + (cx * scale) + sx
                        py = y + (cy * scale) + sy
                        byte_pos = (px // 8) + (py * EPD_WIDTH_BYTES)
                        bit_pos = 7 - (px % 8)
                        
                        if color in (0, 1):
                            gray_buffer[byte_pos] &= ~(1 << bit_pos)
                        if color in (0, 2):
                            black_buffer[byte_pos] &= ~(1 << bit_pos)

@micropython.native
def print_text_scaled(text, x, y, scale, gray_buffer, black_buffer, color=0):
    """Print scaled text string on the display.
    Args:
        text: String to print
        x: Starting X position in pixels
        y: Starting Y position in pixels
        scale: Scaling factor (1 for normal, 2 for double size, etc.)
        gray_buffer: Buffer for gray bits
        black_buffer: Buffer for black bits
        color: Color value (0=black, 1=dark gray, 2=light gray, 3=white)
    """
    cursor_x = x
    for char in text:
        print_char_scaled(char, cursor_x, y, scale, gray_buffer, black_buffer, color)
        cursor_x += CHAR_WIDTH * scale

def draw_frame(image_data):
    """Draw a frame border on the display.
    Args:
        image_data: Buffer to draw the frame into
    Returns:
        Modified image_data with frame drawn
    """
    # clear buffer
    for i in range(0, EPD_WIDTH_BYTES * EPD_HEIGHT):
        image_data[i] = 0xFF
    # Draw first column
    for i in range(0, EPD_WIDTH_BYTES * EPD_HEIGHT, EPD_WIDTH_BYTES):
        image_data[i] = 0x7F
    # Draw last column
    for i in range(EPD_WIDTH_BYTES - 1, EPD_WIDTH_BYTES * EPD_HEIGHT, EPD_WIDTH_BYTES):
        image_data[i] = 0xFE
    # Draw first row
    for i in range(EPD_WIDTH_BYTES):
        image_data[i] = 0x00
    # Draw last row
    for i in range(EPD_WIDTH_BYTES * (EPD_HEIGHT - 1), EPD_WIDTH_BYTES * EPD_HEIGHT):
        image_data[i] = 0x00
        
    return image_data

def load_raw_image(buffer, x, y, byte_width, filename, image_width, image_height):
    """Load a raw image file into a bytearray.
    Args:
        buffer: Buffer to load the image into
        x: X position in pixels in buffer
        y: Y position in pixels in buffer
        byte_width: Width of the buffer in bytes
        filename: Path to the image file
        image_width: Width of the image in pixels
        image_height: Height of the image in pixels
    Returns:
        Bytearray containing the image data
    """
    try:
        # Calculate bytes needed for image width (rounded up to nearest byte)
        image_byte_width = (image_width + 7) // 8
        
        # Open file in binary mode
        with open(filename, 'rb') as f:
            for row in range(image_height):
                if y + row >= EPD_HEIGHT:
                    break
                    
                # Read one row of image data
                row_data = f.read(image_byte_width)
                if not row_data:
                    break
                    
                # Calculate destination position in buffer
                dest_y = y + row
                dest_x_byte = x // 8
                x_offset = x % 8
                
                # Process each byte in the row
                for col_byte in range(min(image_byte_width, (EPD_WIDTH_BYTES * 8 - x) // 8)):
                    if dest_x_byte + col_byte >= byte_width:
                        break
                        
                    src_byte = row_data[col_byte]
                    
                    # If x is byte-aligned, simple copy
                    if x_offset == 0:
                        buffer[dest_x_byte + col_byte + dest_y * byte_width] = src_byte
                    else:
                        # Handle unaligned x position by shifting bits
                        curr_byte = (src_byte >> x_offset)
                        if dest_x_byte + col_byte < byte_width:
                            buffer[dest_x_byte + col_byte + dest_y * byte_width] &= ~(0xFF >> x_offset)
                            buffer[dest_x_byte + col_byte + dest_y * byte_width] |= curr_byte
                            
                        # Handle overflow bits to next byte
                        if x_offset and (dest_x_byte + col_byte + 1) < byte_width:
                            next_byte = (src_byte << (8 - x_offset)) & 0xFF
                            buffer[dest_x_byte + col_byte + 1 + dest_y * byte_width] &= ~(0xFF << (8 - x_offset))
                            buffer[dest_x_byte + col_byte + 1 + dest_y * byte_width] |= next_byte
                            
        return buffer
        
    except OSError as e:
        print("Error loading image:", e)
        return buffer
