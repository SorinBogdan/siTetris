import re
import time
import argparse

from luma.led_matrix.device import max7219
from luma.core.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

def demo(n, block_orientation):
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation)
    #device = max7219(serial, width=8, height=16)
    print("Created device")
    with canvas(device) as draw:
        draw.point((0,1),1)
    
    # start demo
    #msg = "MAX7219 LED Matrix Demo"
    #print(msg)
    #show_message(device, msg, fill="white", font=proportional(CP437_FONT))
    time.sleep(10)

if __name__ == "__main__":
    demo(2,90)
