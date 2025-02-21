import tkinter as tk
from tkinter import messagebox
import os
import shutil
import sys

def setup_images():
    """Prompt for Bongo type and Light/Dark mode."""
    setup_window = tk.Tk()
    setup_window.title("Bongo Setup: Select Type & Theme")
    
    # Variables for radio buttons.
    bongo_type = tk.StringVar(value="Keyboard")
    bongo_mode = tk.StringVar(value="Light")
    
    # Frame for Bongo Type selection.
    type_frame = tk.LabelFrame(setup_window, text="Select Bongo Type")
    type_frame.pack(padx=10, pady=10, fill="both", expand=True)
    tk.Radiobutton(type_frame, text="Keyboard Bongo", variable=bongo_type, value="Keyboard").pack(anchor="w")
    tk.Radiobutton(type_frame, text="Table Bongo", variable=bongo_type, value="Table").pack(anchor="w")
    
    # Frame for Theme selection.
    mode_frame = tk.LabelFrame(setup_window, text="Select Theme")
    mode_frame.pack(padx=10, pady=10, fill="both", expand=True)
    tk.Radiobutton(mode_frame, text="Light Mode", variable=bongo_mode, value="Light").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="Dark Mode", variable=bongo_mode, value="Dark").pack(anchor="w")
    
    def on_confirm():
        setup_window.destroy()
    
    confirm_button = tk.Button(setup_window, text="Confirm", command=on_confirm)
    confirm_button.pack(pady=10)
    
    setup_window.mainloop()
    return bongo_type.get(), bongo_mode.get()

def copy_images(selected_type, selected_mode):
    """Copy images from the chosen folder into the root directory."""
    # Determine source folder based on user selection.
    if selected_type == "Keyboard":
        folder = "Gud Bongo" if selected_mode == "Light" else "Evul Ognob"
    else:  # Table
        folder = "Table Bongo Light" if selected_mode == "Light" else "Table Bongo Dark"
    
    if not os.path.exists(folder):
        messagebox.showerror("Error", f"Image folder '{folder}' not found!")
        return False
    
    # Overwrite the 1.png through 10.png files in the root.
    for i in range(1, 11):
        src = os.path.join(folder, f"{i}.png")
        dst = f"{i}.png"
        if os.path.exists(src):
            shutil.copy(src, dst)
        else:
            messagebox.showerror("Error", f"File {src} not found!")
            return False
    return True

# First, run the setup prompt.
selected_type, selected_mode = setup_images()
if not copy_images(selected_type, selected_mode):
    sys.exit(1)

# Now create the main mode-selection window.
def run_rhythm():
    root.destroy()  # Close the prompt window.
    import BongoRhythm
    BongoRhythm.run()

def run_typing():
    root.destroy()
    import BongoTyping
    BongoTyping.run()

root = tk.Tk()
root.title("Select Mode")

# Set window dimensions and center the window.
window_width = 300
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)

# Create buttons for each mode.
btn_rhythm = tk.Button(root, text="Bongo Rhythm", command=run_rhythm, width=20, height=2)
btn_rhythm.pack(pady=10)
btn_typing = tk.Button(root, text="Bongo Typing", command=run_typing, width=20, height=2)
btn_typing.pack(pady=10)

root.mainloop()
