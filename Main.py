import tkinter as tk
import sys
import pygame
import threading
from pynput import keyboard
import win32gui
import win32con
import win32api
import time
import os
import json

def run_rhythm():
    root.destroy()  # Close the prompt window.
    # Import and run BongoMAX.
    import BongoRhythm
    BongoRhythm.run()

def run_typing():
    root.destroy()  # Close the prompt window.
    # Import and run BongoTyping.
    import BongoTyping
    BongoTyping.run()

# Create the main Tkinter window.
root = tk.Tk()
root.title("Select Mode")

# Set the dimensions for the prompt window.
window_width = 300
window_height = 150

# Calculate the center of the screen.
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the geometry of the window so that it appears centered.
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)

# Create and place the buttons.
btn_rhythm = tk.Button(root, text="Bongo Rhythm", command=run_rhythm, width=20, height=2)
btn_rhythm.pack(pady=10)

btn_typing = tk.Button(root, text="Bongo Typing", command=run_typing, width=20, height=2)
btn_typing.pack(pady=10)

# Start the Tkinter event loop.
root.mainloop()
