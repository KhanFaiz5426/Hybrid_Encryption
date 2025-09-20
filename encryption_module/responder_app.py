import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import json
import base64
import os
import sys

# --- Allow the script to find the 'encryption_module' ---
try:
    from encryption_module import decrypt_message, load_private_key
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from encryption_module import decrypt_message, load_private_key

# --- Configuration ---
KEY_PATH = "keys/responder_private.pem"
PACKAGE_PATH = "sos_package.json"

class ResponderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Key Loading ---
        self.responder_private_key = self.load_key()
        if not self.responder_private_key:
            messagebox.showerror("Key Error", f"Could not load private key from:\n{KEY_PATH}\n\nPlease run generate_keys.py first.")
            self.destroy()
            return

        # --- Window Setup ---
        self.title("Responder Decryption App")
        self.geometry("500x450")
        self.configure(bg="#2c3e50")
        self.resizable(False, False)

        # --- Font Setup ---
        self.title_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.text_font = font.Font(family="Helvetica", size=12)
        self.status_font = font.Font(family="Helvetica", size=11, weight="bold")

        # --- UI Creation ---
        self.create_widgets()

    def load_key(self):
        try:
            return load_private_key(KEY_PATH)
        except FileNotFoundError:
            return None

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#2c3e50")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = tk.Label(main_frame, text="Incoming SOS", font=self.title_font, fg="#ecf0f1", bg="#2c3e50")
        title_label.pack(pady=(0, 20))

        # --- Decrypt Button ---
        decrypt_button = tk.Button(main_frame, text="Decrypt Last SOS Package", font=self.button_font,
                                   bg="#27ae60", fg="white", relief="flat", pady=10,
                                   command=self.decrypt_sos_package)
        decrypt_button.pack(pady=10, fill="x")

        # --- Message Display Area ---
        self.message_display = scrolledtext.ScrolledText(main_frame, height=10, width=50,
                                                         font=self.text_font, bg="#34495e", fg="#ecf0f1",
                                                         relief="flat", insertbackground="#ecf0f1", bd=10,
                                                         state="disabled")
        self.message_display.pack(pady=10, fill="both", expand=True)

        # --- Status Label ---
        self.status_label = tk.Label(self, text="Status: Ready to decrypt", font=self.status_font,
                                     fg="white", bg="#3498db", pady=5)
        self.status_label.pack(side="bottom", fill="x")

    def decrypt_sos_package(self):
        """Reads, decodes, and decrypts the package file, then displays the result."""
        self.clear_display()
        try:
            # Step 1: Read the package file
            with open(PACKAGE_PATH, "r") as f:
                package = json.load(f)

            # Step 2: Convert base64 strings back to bytes
            decoded_package = {
                key: base64.b64decode(value)
                for key, value in package.items()
            }
            
            # Step 3: Decrypt the message
            decrypted_message = decrypt_message(self.responder_private_key, decoded_package)
            
            # Step 4: Display the result
            self.update_display(f"--- DECRYPTED MESSAGE ---\n\n{decrypted_message}")
            self.update_status("✅ SOS Decrypted Successfully!", "#27ae60")
            print(f"[Responder] Decrypted SOS: {decrypted_message}")

        except FileNotFoundError:
            error_msg = f"Error: The SOS package file was not found.\n\nMake sure '{PACKAGE_PATH}' exists."
            self.update_display(error_msg)
            self.update_status(f"❌ Error: '{PACKAGE_PATH}' not found", "#e74c3c")
            print(f"[Responder] Error: {PACKAGE_PATH} not found.")
        except Exception as e:
            error_msg = f"A decryption error occurred.\n\nDetails: {e}"
            self.update_display(error_msg)
            self.update_status("❌ Decryption Failed!", "#e74c3c")
            print(f"[Responder] Decryption failed: {e}")

    def update_status(self, text, color):
        """Updates the status bar."""
        self.status_label.config(text=text, bg=color)

    def update_display(self, text):
        """Puts text into the main display area."""
        self.message_display.config(state="normal")
        self.message_display.delete("1.0", tk.END)
        self.message_display.insert("1.0", text)
        self.message_display.config(state="disabled")

    def clear_display(self):
        self.update_display("")

if __name__ == "__main__":
    app = ResponderApp()
    app.mainloop()
