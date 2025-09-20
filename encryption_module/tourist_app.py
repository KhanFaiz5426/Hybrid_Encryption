import tkinter as tk
from tkinter import messagebox, font
import json
import socket
import base64
import sys
import os

# --- This allows the script to find the 'encryption_module' if it's in the parent directory ---
try:
    from encryption_module import encrypt_message, load_public_key
except ImportError:
    # If the script is run from the root folder, this might be needed.
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from encryption_module import encrypt_message, load_public_key

# --- Configuration ---
# NOTE: Your new server.py is hardcoded to "localhost".
# If you change it to "0.0.0.0" later, you will need to change this IP address.
SERVER_HOST = "127.0.0.1"  # Connects to localhost
SERVER_PORT = 5000
KEY_PATH = "keys/responder_public.pem"

# --- Main Application Class ---
class TouristApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # --- Key Loading ---
        self.responder_public_key = self.load_key()
        if not self.responder_public_key:
            messagebox.showerror("Key Error", f"Could not load public key from:\n{KEY_PATH}\n\nPlease run generate_keys.py first.")
            self.destroy()
            return

        # --- Window Setup ---
        self.title("Tourist Emergency SOS")
        self.geometry("500x600")
        self.configure(bg="#2c3e50") # Dark blue background
        self.resizable(False, False)

        # --- Font Setup ---
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.status_font = font.Font(family="Helvetica", size=11, weight="bold")

        # --- UI Creation ---
        self.create_widgets()

    def load_key(self):
        """Loads the RSA public key from the specified path."""
        try:
            return load_public_key(KEY_PATH)
        except FileNotFoundError:
            return None

    def create_widgets(self):
        """Creates and arranges all the UI elements in the window."""
        main_frame = tk.Frame(self, bg="#2c3e50")
        main_frame.pack(pady=30, padx=30, fill="both", expand=True)

        # --- Title ---
        title_label = tk.Label(main_frame, text="Emergency SOS", font=self.title_font, fg="#ecf0f1", bg="#2c3e50")
        title_label.pack(pady=(0, 20))

        # --- Message Entry ---
        msg_label = tk.Label(main_frame, text="Describe your emergency below:", font=self.label_font, fg="#bdc3c7", bg="#2c3e50")
        msg_label.pack(anchor="w")

        self.message_text = tk.Text(main_frame, height=5, width=50, font=self.label_font, bg="#34495e", fg="#ecf0f1", relief="flat", insertbackground="#ecf0f1", bd=10)
        self.message_text.pack(pady=10)
        
        # --- Quick SOS Buttons ---
        quick_sos_frame = tk.Frame(main_frame, bg="#2c3e50")
        quick_sos_frame.pack(pady=15)
        
        quick_sos_label = tk.Label(quick_sos_frame, text="Or send a quick alert:", font=self.label_font, fg="#bdc3c7", bg="#2c3e50")
        quick_sos_label.pack(anchor="w", pady=(0, 10))

        buttons_frame = tk.Frame(quick_sos_frame, bg="#2c3e50")
        buttons_frame.pack()

        btn_style = {'font': self.label_font, 'bg': "#3498db", 'fg': "white", 'relief': "flat", 'width': 18, 'pady': 5}
        quick_messages = ["Medical Assistance Needed", "Lost / Need Directions", "Theft or Robbery Report"]
        
        tk.Button(buttons_frame, text=quick_messages[0], **btn_style, command=lambda: self.send_sos(quick_messages[0])).grid(row=0, column=0, padx=5)
        tk.Button(buttons_frame, text=quick_messages[1], **btn_style, command=lambda: self.send_sos(quick_messages[1])).grid(row=0, column=1, padx=5)
        tk.Button(buttons_frame, text=quick_messages[2], **btn_style, command=lambda: self.send_sos(quick_messages[2])).grid(row=1, column=0, columnspan=2, pady=10)

        # --- Main Send Button ---
        send_button = tk.Button(main_frame, text="🚨 SEND MY MESSAGE 🚨", font=self.button_font, bg="#e74c3c", fg="white", relief="flat", pady=15, command=self.send_custom_sos)
        send_button.pack(pady=20, fill="x")

        # --- Status Label ---
        self.status_label = tk.Label(self, text="Status: Ready", font=self.status_font, fg="white", bg="#27ae60", pady=5)
        self.status_label.pack(side="bottom", fill="x")

    def send_custom_sos(self):
        """Gets message from the text box and sends it."""
        message = self.message_text.get("1.0", tk.END).strip()
        self.send_sos(message)

    def send_sos(self, message):
        """Encrypts the message and sends the complete JSON package to the server."""
        if not message.strip():
            self.update_status("⚠️ Please enter a message!", "orange")
            return

        try:
            # Step 1: Encrypt the plaintext message using the responder's public key.
            # This returns a dictionary with values as raw bytes.
            package = encrypt_message(self.responder_public_key, message)

            # Step 2: Convert the raw bytes into Base64 encoded strings.
            # This makes the data safe to be put into a JSON file.
            safe_package = {
                "encrypted_key": base64.b64encode(package["encrypted_key"]).decode('utf-8'),
                "ciphertext": base64.b64encode(package["ciphertext"]).decode('utf-8'),
                "nonce": base64.b64encode(package["nonce"]).decode('utf-8'),
            }
            
            # Step 3: Convert the dictionary into a single JSON string.
            json_payload = json.dumps(safe_package)

            # Step 4: Send the JSON string to the server.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((SERVER_HOST, SERVER_PORT))
                client.sendall(json_payload.encode('utf-8'))
            
           # print(f"[Tourist] Sent encrypted package for message: '{message}'")
            self.update_status("✅ SOS Sent Securely!", "#27ae60")

        except ConnectionRefusedError:
            self.update_status("❌ Connection Failed. Is the server running?", "#c0392b")
            print("[Tourist] Connection refused. Server might not be running.")
        except Exception as e:
            self.update_status(f"❌ An error occurred: {e}", "#c0392b")
            print(f"[Tourist] An error occurred: {e}")

    def update_status(self, text, color):
        """Updates the status bar with a message and color."""
        self.status_label.config(text=text, bg=color)


if __name__ == "__main__":
    app = TouristApp()
    app.mainloop()
