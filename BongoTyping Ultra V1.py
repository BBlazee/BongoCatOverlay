import pygame
import threading
from pynput import keyboard
import win32gui
import win32con
import win32api
import time
import os

# ---------------------------
# INITIAL WINDOW SETUP
# ---------------------------
# Default overlay size: 640x320.
window_width = 640
window_height = 320
# Initial window position.
window_x, window_y = 100, 100

pygame.init()
# Define a custom event for resizing.
RESIZE_EVENT = pygame.USEREVENT + 1

screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
pygame.display.set_caption("Bongo Cat Typing")
time.sleep(0.5)

# Get the window handle so we can force it always on top and move it.
hwnd = win32gui.FindWindow(None, "Bongo Cat Typing")
def set_window_pos(x, y):
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0, win32con.SWP_NOSIZE)
set_window_pos(window_x, window_y)
window_locked = False  # Used for window locking

def move_window(dx, dy):
    global window_x, window_y, window_locked
    if window_locked:
        return  # Do not move if locked.
    window_x += dx
    window_y += dy
    set_window_pos(window_x, window_y)

# ---------------------------
# PRECONFIGURED KEY SEGMENTS & MAPPINGS
# ---------------------------
KEY_SEGMENTS = {
    "Segment 1": "\x1b\t\x14\x10\x11\x12" "12qwaszx",  # Left-most keys.
    "Segment 2": "34erdfcv",
    "Segment 3": "56tyghbn",
    "Segment 4": "78uijkm,<",
    "Segment 5": "90opl:>",
    "Segment 6": "-=\\[];',./`~!@#$%^&*()_+{}|:\"<>?" + "\b\r\x7f\x0d\x1c\x1d\x1e\x1f",
    "Segment 7": " "  # Spacebar
}
KEY_MAPPINGS = {
    "Segment 1": 1,
    "Segment 2": 2,
    "Segment 3": 3,
    "Segment 4": 4,
    "Segment 5": 5,
    "Segment 6": 6,
    "Segment 7": 10
}

def get_segment(key):
    try:
        if hasattr(key, 'char') and key.char:
            ch = key.char.lower()
            for segment, chars in KEY_SEGMENTS.items():
                if ch in chars:
                    return segment
        if key == keyboard.Key.space:
            return "Segment 7"
        if key in [keyboard.Key.esc, keyboard.Key.tab, keyboard.Key.caps_lock,
                   keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt]:
            return "Segment 1"
        if key in [keyboard.Key.backspace, keyboard.Key.enter,
                   keyboard.Key.shift_r, keyboard.Key.ctrl_r, keyboard.Key.alt_r]:
            return "Segment 6"
    except Exception:
        return None
    return None

# ---------------------------
# LOAD & SCALE IMAGES
# ---------------------------
# Load raw images (assumed to be 640x320 originally).
raw_images = {i: pygame.image.load(f"{i}.png") for i in range(1, 11)}
# Scale the raw images to the initial window size.
images = {i: pygame.transform.scale(raw_images[i],1 (window_width, window_height))
          for i in raw_images}
current_image = images[1]

# ---------------------------
# UPDATE DISPLAYED IMAGE
# ---------------------------
pressed_keys = set()
def update_image():
    global current_image
    segments = [get_segment(key) for key in pressed_keys if get_segment(key)]
    if segments:
        current_image = images[KEY_MAPPINGS[segments[-1]]]
    else:
        current_image = images[9]

# ---------------------------
# FUNCTION TO RESIZE THE OVERLAY WHILE MAINTAINING ASPECT RATIO
# ---------------------------
def resize_overlay(new_width, new_height):
    global window_width, window_height, screen, images
    # Get the original aspect ratio from one of the raw images.
    raw_w, raw_h = raw_images[1].get_size()
    aspect_ratio = raw_w / raw_h  # For 640x320, this is 2:1.
    
    # Adjust new_width and new_height to respect the aspect ratio.
    # Here we choose the dimension that keeps the ratio intact.
    if new_width / new_height > aspect_ratio:
        new_width = int(new_height * aspect_ratio)
    else:
        new_height = int(new_width / aspect_ratio)
    
    window_width, window_height = new_width, new_height
    screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
    # Re-scale all images from the raw images.
    images = {i: pygame.transform.scale(raw_images[i], (window_width, window_height))
              for i in raw_images}
    print(f"Resized window to: {window_width}x{window_height}")

# ---------------------------
# KEYBOARD LISTENER HANDLERS (pynput)
# ---------------------------
def on_press(key):
    global window_locked
    if key == keyboard.Key.f9:
        window_locked = not window_locked
        print("Window locked." if window_locked else "Window unlocked.")
        return

    # Resize overlay using F8 (increase size) and F7 (decrease size).
    if key == keyboard.Key.f8:
        # Increase size by 10%.
        new_width = int(window_width * 1.1)
        new_height = int(window_height * 1.1)
        pygame.event.post(pygame.event.Event(RESIZE_EVENT, {'width': new_width, 'height': new_height}))
        return
    elif key == keyboard.Key.f7:
        # Decrease size by 10% with a minimum limit.
        new_width = max(100, int(window_width / 1.1))
        new_height = max(100, int(window_height / 1.1))
        pygame.event.post(pygame.event.Event(RESIZE_EVENT, {'width': new_width, 'height': new_height}))
        return

    seg = get_segment(key)
    if seg:
        pressed_keys.add(key)
        update_image()
    
    if key == keyboard.Key.up:
        move_window(0, -32)
    elif key == keyboard.Key.down:
        move_window(0, 32)
    elif key == keyboard.Key.left:
        move_window(-32, 0)
    elif key == keyboard.Key.right:
        move_window(32, 0)

def on_release(key):
    if key in pressed_keys:
        pressed_keys.remove(key)
        update_image()

def input_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

threading.Thread(target=input_listener, daemon=True).start()

# ---------------------------
# MAIN PYGAME LOOP
# ---------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == RESIZE_EVENT:
            new_width = event.width
            new_height = event.height
            resize_overlay(new_width, new_height)
    
    screen.fill((0, 0, 0))
    screen.blit(current_image, (0, 0))
    pygame.display.flip()

pygame.quit()
