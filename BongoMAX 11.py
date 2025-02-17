import pygame
import threading
from pynput import keyboard
import win32gui
import win32con
import win32api
import time
import os
import json

# ---------------------------
# Determine Screen Resolution & Scale Factor
# ---------------------------
# Our "base" resolution is 2560×1440.
screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)
# Compute a scale factor so that if the user's screen is 2560x1440, factor is 1,
# or if 1920x1080, factor is 0.75 (we use the minimum so that everything fits).
scale_factor = min(screen_width / 2560, screen_height / 1440)

# Our base window size is 640×320 and base window position is (960, 1100).
window_width = int(640 * scale_factor)
window_height = int(320 * scale_factor)
window_x = int(960 * scale_factor)
window_y = int(1100 * scale_factor)

# ---------------------------
# Pygame Initialization and Window Setup
# ---------------------------
pygame.init()
screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
pygame.display.set_caption("Bongo MAX")
time.sleep(0.5)

# Get the handle of the Pygame window for setting always-on-top and moving.
hwnd = win32gui.FindWindow(None, "Bongo MAX")

def set_window_pos(x, y):
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0, win32con.SWP_NOSIZE)

# Position the window using our scaled coordinates.
set_window_pos(window_x, window_y)
window_locked = False  # Global flag to lock window movement.

def move_window(dx, dy):
    global window_x, window_y, window_locked
    if window_locked:
        return
    # Multiply movement increments by the scale_factor so the feel is consistent.
    window_x += int(dx * scale_factor)
    window_y += int(dy * scale_factor)
    set_window_pos(window_x, window_y)

# ---------------------------
# Key Normalization Helpers
# ---------------------------
# For configuration (Pygame), we want to capture all keys (including modifiers)
# and also distinguish keypad keys.
SPECIAL_KEYS_MAP = {
    pygame.K_LSHIFT: "Key.shift_l",
    pygame.K_RSHIFT: "Key.shift_r",
    pygame.K_LCTRL:  "Key.ctrl_l",
    pygame.K_RCTRL:  "Key.ctrl_r",
    pygame.K_LALT:   "Key.alt_l",
    pygame.K_RALT:   "Key.alt_r",
    # Add function keys or others as needed.
}

# Also, we want keypad keys to be mapped to their Windows virtual-key codes.
KEYPAD_MAP = {
    pygame.K_KP0: 96,
    pygame.K_KP1: 97,
    pygame.K_KP2: 98,
    pygame.K_KP3: 99,
    pygame.K_KP4: 100,
    pygame.K_KP5: 101,
    pygame.K_KP6: 102,
    pygame.K_KP7: 103,
    pygame.K_KP8: 104,
    pygame.K_KP9: 105,
    pygame.K_KP_PLUS: 107,
}

def normalize_pygame_key(event):
    """
    Returns a normalized key identifier (a string) for Pygame events.
    Uses SPECIAL_KEYS_MAP for modifiers, KEYPAD_MAP for keypad keys,
    otherwise returns the lower-case unicode if available,
    or falls back to pygame.key.name (with adjustments for arrow keys).
    """
    if event.key in SPECIAL_KEYS_MAP:
        return SPECIAL_KEYS_MAP[event.key]
    if event.key in KEYPAD_MAP:
        return str(KEYPAD_MAP[event.key])
    if event.unicode and event.unicode.strip() != "":
        return event.unicode.lower()
    # Fallback: use pygame.key.name and adjust common names.
    name = pygame.key.name(event.key)
    if name in ["up", "down", "left", "right"]:
        return "Key." + name
    if name == "left shift":
        return "Key.shift_l"
    elif name == "right shift":
        return "Key.shift_r"
    elif name == "left ctrl":
        return "Key.ctrl_l"
    elif name == "right ctrl":
        return "Key.ctrl_r"
    elif name == "left alt":
        return "Key.alt_l"
    elif name == "right alt":
        return "Key.alt_r"
    return name

def normalize_pynput_key(key):
    """
    Returns a normalized key identifier (a string) for pynput events.
    For special keys (modifiers, function keys, etc.) it uses a "Key.<name>" format,
    and for printable keys it returns the lowercase character.
    Special handling for numpad plus (vk == 107) is provided.
    """
    if isinstance(key, keyboard.Key):
        if key == keyboard.Key.shift:
            return "Key.shift_l"  # Assume left shift if ambiguous.
        return f"Key.{key.name}" if hasattr(key, "name") and key.name is not None else str(key)
    elif isinstance(key, keyboard.KeyCode):
        if key.vk == 107:  # Numpad plus
            return "107"
        if key.char is not None:
            return key.char.lower()
        else:
            return str(key.vk)
    else:
        return str(key)

# ---------------------------
# Prompt to Regenerate Config?
# ---------------------------
def prompt_regenerate_config():
    """
    Displays a prompt on the Pygame window asking:
    "Regenerate input config? (Y/N)"
    Waits for the user to press Y or N, and returns True if Y, False if N.
    """
    font = pygame.font.SysFont(None, 36)
    prompt_text = "Regenerate input config? (Y/N)"
    screen.fill((0, 0, 0))
    text_surface = font.render(prompt_text, True, (255, 255, 255))
    rect = text_surface.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text_surface, rect)
    pygame.display.flip()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            key_id = normalize_pygame_key(event)
            if key_id == "y":
                return True
            elif key_id == "n":
                return False

# ---------------------------
# Configuration Popup for Custom Key Mapping
# ---------------------------
def configure_keys():
    """
    Opens a configuration loop (using the Pygame window) that prompts
    the user to press a key for each note.
    
    The prompts (and corresponding image numbers) are:
      - Left Note 1 → 1.png
      - Left Note 2 → 2.png
      - Left Note 3 → 3.png
      - Right Note 1 → 4.png
      - Right Note 2 → 5.png
      - Right Note 3 → 6.png
      - Side Note Left → 7.png
      - Side Note Right → 8.png
    
    The mapping is then saved as JSON to "key_mapping.txt" in the root folder.
    """
    mapping = {}
    font = pygame.font.SysFont(None, 36)
    instructions = "Configuration: Set your note keys."
    
    # Show initial instructions.
    screen.fill((0, 0, 0))
    text_surface = font.render(instructions, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    pygame.display.flip()
    time.sleep(3)
    
    # List of prompts and corresponding image numbers.
    config_prompts = [
        ("Left Note 1", 1),
        ("Left Note 2", 2),
        ("Left Note 3", 3),
        ("Right Note 1", 4),
        ("Right Note 2", 5),
        ("Right Note 3", 6),
        ("Side Note Left", 7),
        ("Side Note Right", 8)
    ]
    
    for label, image_num in config_prompts:
        screen.fill((0, 0, 0))
        prompt = f"Press key for {label} ({image_num}.png)"
        text_surface = font.render(prompt, True, (255, 255, 255))
        rect = text_surface.get_rect(center=(window_width // 2, window_height // 2))
        screen.blit(text_surface, rect)
        pygame.display.flip()
        
        key_set = False
        while not key_set:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                key_id = normalize_pygame_key(event)
                mapping[key_id] = image_num
                # Provide brief visual feedback.
                screen.fill((0, 0, 0))
                feedback = f"{label} set to: {key_id}"
                fb_surface = font.render(feedback, True, (0, 255, 0))
                fb_rect = fb_surface.get_rect(center=(window_width // 2, window_height // 2))
                screen.blit(fb_surface, fb_rect)
                pygame.display.flip()
                time.sleep(0.5)
                key_set = True

    # Save the mapping for future launches.
    with open("key_mapping.txt", "w") as f:
        json.dump(mapping, f)
    return mapping

# ---------------------------
# Load or (Optionally) Regenerate Custom Mapping
# ---------------------------
if os.path.exists("key_mapping.txt"):
    # Prompt the user whether to regenerate the input config.
    if prompt_regenerate_config():
        custom_mapping = configure_keys()
    else:
        with open("key_mapping.txt", "r") as f:
            custom_mapping = json.load(f)
else:
    custom_mapping = configure_keys()

# ---------------------------
# Load and Scale Images
# ---------------------------
# Load the original 640x320 images and then scale them to the current window size.
# Images 1-8 are for the notes, and image 9 is the resting image.
raw_images = {i: pygame.image.load(f"{i}.png") for i in range(1, 10)}
images = {
    i: pygame.transform.scale(raw_images[i], (window_width, window_height))
    for i in range(1, 10)
}
# Set resting image to image 9.
current_image = images[9]

# ---------------------------
# Button Press State and Image Update
# ---------------------------
pressed_keys = []

def update_image():
    global current_image
    # Look at the most recent pressed key (from our custom mapping) to select an image.
    for key_id in reversed(pressed_keys):
        if key_id in custom_mapping:
            current_image = images[ custom_mapping[key_id] ]
            return
    # Default to resting image.
    current_image = images[9]

# ---------------------------
# pynput Keyboard Listener Handlers
# ---------------------------
def on_press(key):
    global window_locked
    key_id = normalize_pynput_key(key)
    
    # Toggle window lock with the normal "0" key.
    # (Note: Keypad 0 is different since it's mapped via KEYPAD_MAP.)
    if hasattr(key, 'char') and key.char and key.char == '0':
        window_locked = not window_locked
        print("Window locked." if window_locked else "Window unlocked.")
        return

    # If the key is mapped to one of our notes, update pressed_keys.
    if key_id in custom_mapping:
        if key_id not in pressed_keys:
            pressed_keys.append(key_id)
            update_image()

    # Window movement with i, j, k, l (movement increments are scaled).
    if hasattr(key, 'char') and key.char:
        char = key.char.lower()
        if char == 'i':
            move_window(0, -10)
        elif char == 'k':
            move_window(0, 10)
        elif char == 'j':
            move_window(-10, 0)
        elif char == 'l':
            move_window(10, 0)

def on_release(key):
    key_id = normalize_pynput_key(key)
    if key_id in pressed_keys:
        pressed_keys.remove(key_id)
        update_image()

def input_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Start the pynput listener in a separate thread.
threading.Thread(target=input_listener, daemon=True).start()

# ---------------------------
# Main Pygame Loop
# ---------------------------
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(current_image, (0, 0))
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()