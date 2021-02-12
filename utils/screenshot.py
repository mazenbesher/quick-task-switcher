from PIL import Image
from mss import mss


def save_screenshot(mon_idx: int = 0, output_fname: str = 'screenshot.png', new_size=(256, 256)):
    """mon_idx=0 => all monitors"""
    with mss() as sct:
        mon = sct.monitors[mon_idx]
        sct_img = sct.grab(mon)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.thumbnail(new_size, Image.ANTIALIAS)
        img.save(output_fname)
