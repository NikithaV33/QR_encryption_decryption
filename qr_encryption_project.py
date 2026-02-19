import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet
import qrcode
import cv2
import os

# Initialize main window
root = tk.Tk()
root.title("QR Code Encryption Tool")
root.geometry("650x700")
root.config(bg="#f9f9f9")

# Global variables
cipher = None
key = None
encrypted_text = ""
qr_filename = "encrypted_qr.png"


# Step 1: Generate encryption key
def generate_key():
    global key, cipher
    key = Fernet.generate_key()
    cipher = Fernet(key)
    key_entry.delete(0, tk.END)
    key_entry.insert(0, key.decode())
    messagebox.showinfo("Key Generated", "A new encryption key has been created!")


# Step 2: Encrypt text and generate QR (save only, not display)
def encrypt_and_generate_qr():
    global encrypted_text, qr_filename
    message = message_entry.get("1.0", tk.END).strip()
    if not message or not cipher:
        messagebox.showerror("Error", "Please generate a key and enter a message!")
        return

    encrypted_text = cipher.encrypt(message.encode()).decode()

    # Ask user where to save
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="Save QR Code As"
    )
    if not save_path:
        return
    qr_filename = save_path

    # Save QR without showing in GUI
    img = qrcode.make(encrypted_text)
    img.save(qr_filename)

    messagebox.showinfo("Success", f"QR code saved as:\n{qr_filename}")


# Step 3: Decode and decrypt from uploaded/generated QR
def decode_and_decrypt(qr_path=None):
    global cipher
    if not cipher:
        messagebox.showerror("Error", "Please generate or enter the encryption key first!")
        return

    if not qr_path and not os.path.exists(qr_filename):
        messagebox.showerror("Error", "No QR code found! Generate or upload one first.")
        return

    path_to_read = qr_path if qr_path else qr_filename

    detector = cv2.QRCodeDetector()
    val, pts, _ = detector.detectAndDecode(cv2.imread(path_to_read))
    if not val:
        messagebox.showerror("Error", "Could not read QR code.")
        return

    try:
        decrypted = cipher.decrypt(val.encode()).decode()
        decrypted_text.delete("1.0", tk.END)
        decrypted_text.insert(tk.END, decrypted)
        messagebox.showinfo("Success", "Message successfully decrypted!")
    except Exception:
        messagebox.showerror("Decryption Failed", "Invalid key or QR data!")


# Step 4: Upload and scan QR
def upload_qr():
    file_path = filedialog.askopenfilename(
        filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")],
        title="Select a QR Code Image"
    )
    if not file_path:
        return

    decode_and_decrypt(file_path)


# --- GUI Layout ---
tk.Label(root, text="🔐 QR Code Encryption & Decryption", font=("Arial", 17, "bold"), bg="#f9f9f9").pack(pady=10)

# Key Section
tk.Label(root, text="Encryption Key:", bg="#f9f9f9", font=("Arial", 11, "bold")).pack()
key_entry = tk.Entry(root, width=60)
key_entry.pack(pady=5)
tk.Button(root, text="Generate Key", command=generate_key, bg="#4CAF50", fg="white", width=20).pack(pady=5)

# Message Input
tk.Label(root, text="Enter your secret message:", bg="#f9f9f9", font=("Arial", 11, "bold")).pack(pady=5)
message_entry = tk.Text(root, height=4, width=60)
message_entry.pack(pady=5)

# Generate QR
tk.Button(root, text="Encrypt & Generate QR", command=encrypt_and_generate_qr, bg="#2196F3", fg="white", width=25).pack(pady=10)

# Upload and Scan
tk.Button(root, text="📤 Upload Existing QR & Scan", command=upload_qr, bg="#9C27B0", fg="white", width=25).pack(pady=10)

# Decrypted Message Display
tk.Label(root, text="Decrypted Message:", bg="#f9f9f9", font=("Arial", 11, "bold")).pack(pady=5)
decrypted_text = tk.Text(root, height=4, width=60)
decrypted_text.pack(pady=5)

# Exit Button
tk.Button(root, text="Exit", command=root.quit, bg="#E91E63", fg="white", width=15).pack(pady=15)

root.mainloop()

