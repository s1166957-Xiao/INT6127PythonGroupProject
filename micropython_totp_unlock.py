# Flipper Zero TOTP (Time-Based One-Time Password) Viewer
# This script is designed to run in the uPython graphical environment.

import time
import ustruct
import uhmac
import uhashlib
import flipperzero as f0

# --- Simple Base32 Decode ---
# MicroPython's 'ubinascii' does not include b32decode, so a lightweight
# implementation is provided here.
BASE32_ALPHABET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

def b32decode(s):
    """Decodes a Base32 encoded string to bytes."""
    s = s.upper().encode('ascii')
    res = bytearray()
    quanta_len = 0
    quanta = 0
    for c in s:
        if c == ord('='): # Padding character
            break
        val = BASE32_ALPHABET.find(c)
        if val == -1:
            raise ValueError("Invalid character in Base32 string")
        quanta = (quanta << 5) | val
        quanta_len += 5
        if quanta_len >= 8:
            res.append((quanta >> (quanta_len - 8)) & 0xFF)
            quanta_len -= 8
    return bytes(res)

# --- TOTP Generation ---

def get_totp(secret_key, interval=30):
    """
    Calculates the Time-Based One-Time Password (TOTP).

    Args:
        secret_key (str): The Base32 encoded secret key.
        interval (int): The time step in seconds (default is 30).

    Returns:
        str: A 6-digit TOTP code, or "ERROR" if the key is invalid.
    """
    try:
        decoded_key = b32decode(secret_key)
    except Exception:
        return "KEY ERR"

    counter = time.time() // interval
    counter_bytes = ustruct.pack('>Q', int(counter))
    hmac_hash = uhmac.new(decoded_key, counter_bytes, uhashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0F
    truncated_hash = hmac_hash[offset:offset+4]
    code = ustruct.unpack('>I', truncated_hash)[0]
    code &= 0x7FFFFFFF
    code %= 1000000
    return '{:06d}'.format(code)

# --- Flipper Zero Application Setup ---

# Global flag to control the main loop.
should_exit = False

@f0.on_input
def input_handler(button, type):
    """Handles input to exit the app. Exit on a long press of the BACK button."""
    global should_exit
    if button == f0.INPUT_BUTTON_BACK and type == f0.INPUT_TYPE_LONG:
        should_exit = True

def draw_display(totp_code, remaining_time):
    """Draws the TOTP code and countdown on the Flipper screen."""
    f0.canvas_clear()
    
    # Set font and alignment for the main TOTP code
    f0.canvas_set_font(f0.FONT_SECONDARY) # A larger font
    f0.canvas_set_text_align(f0.ALIGN_CENTER, f0.ALIGN_CENTER)
    f0.canvas_set_text(64, 22, "TOTP Code:")
    
    f0.canvas_set_font(f0.FONT_PRIMARY) # The biggest font
    f0.canvas_set_text_align(f0.ALIGN_CENTER, f0.ALIGN_CENTER)
    f0.canvas_set_text(64, 36, totp_code)

    # Draw the countdown bar
    bar_width = int((remaining_time / 30) * 124) # 124 pixels wide bar
    f0.canvas_draw_frame(2, 54, 124, 8)
    f0.canvas_draw_box(3, 55, bar_width - 2, 6)

    f0.canvas_update()

# --- Main Program ---

def run_viewer():
    """Main loop for the Flipper Zero TOTP application."""
    
    # Your secret key.
    SECRET = "WVMBDX4GZ3VOHCKBMVVBJQHGOUNN2535"
    
    # IMPORTANT: Ensure Flipper's RTC is set correctly for TOTP to work.
    
    while not should_exit:
        current_epoch_time = time.time()
        remaining_time = 30 - (current_epoch_time % 30)
        
        totp_code = get_totp(SECRET)
        
        draw_display(totp_code, remaining_time)
        
        time.sleep_ms(250) # Update 4 times per second

# To run the viewer, call the main function.
if __name__ == "__main__":
    run_viewer()