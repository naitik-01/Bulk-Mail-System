import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet

# Load encryption key
with open("key.key", "rb") as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Retrieve credentials from database
conn = sqlite3.connect("email_credentials.db")
cursor = conn.cursor()
cursor.execute("SELECT email, encrypted_password FROM credentials")
result = cursor.fetchone()
conn.close()

# Decrypt stored password
sender_email = result[0]
sender_password = cipher.decrypt(result[1]).decode()

# Function to send emails to multiple recipients
def send_email():
    recipient_emails = recipient_text.get("1.0", tk.END).strip().split("\n")
    subject = subject_entry.get()
    message_body = message_text.get("1.0", tk.END)

    if not recipient_emails or not subject or not message_body.strip():
        messagebox.showerror("Error", "All fields are required!")
        return

    # Allow HTML content (rich text)
    message_body = f"<html><body>{message_body}</body></html>"

    # Create the message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject

    # Attach the message body (HTML format)
    msg.attach(MIMEText(message_body, 'html'))

    # Attach files if selected
    if media_files:
        for file in media_files:
            try:
                part = MIMEBase('application', 'octet-stream')
                with open(file, 'rb') as f:
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={file}')
                msg.attach(part)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to attach file: {e}")
                return

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        for recipient in recipient_emails:
            msg['To'] = recipient.strip()
            server.sendmail(sender_email, recipient.strip(), msg.as_string())

        server.quit()

        messagebox.showinfo("Success", f"Email sent to {len(recipient_emails)} recipients!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")

# File selection dialog for attachments
def select_files():
    global media_files
    filetypes = [("All Files", "*.*"), ("Image Files", "*.jpg;*.jpeg;*.png"), 
                 ("Audio Files", "*.mp3;*.wav"), ("Video Files", "*.mp4;*.avi")]
    media_files = filedialog.askopenfilenames(title="Select Media Files", filetypes=filetypes)
    media_label.config(text=f"{len(media_files)} file(s) selected")

# Function to toggle bold formatting
def toggle_bold():
    global bold
    bold = not bold  # Toggle bold state
    update_style()

# Function to toggle italic formatting
def toggle_italic():
    global italic
    italic = not italic  # Toggle italic state
    update_style()

# Function to toggle underline formatting
def toggle_underline():
    global underline
    underline = not underline  # Toggle underline state
    update_style()

# Function to update style dynamically based on button states
def update_style():
    # Get the current style (if any) and apply the new styles
    style = []
    if bold:
        style.append('bold')
    if italic:
        style.append('italic')
    if underline:
        style.append('underline')

    # Apply the new style to the text widget
    text_widget.tag_configure("current_style", font=("Helvetica", 12, *style))
    text_widget.tag_add("current_style", "insert linestart", "insert lineend")

# GUI Setup
root = tk.Tk()
root.title("Mass Email Sender with Media and Formatting")

tk.Label(root, text="Recipient Emails (One per Line):").pack()
recipient_text = tk.Text(root, width=50, height=10)
recipient_text.pack()

tk.Label(root, text="Subject:").pack()
subject_entry = tk.Entry(root, width=50)
subject_entry.pack()

tk.Label(root, text="Message (Use HTML for styling):").pack()
message_text = tk.Text(root, width=50, height=10)
message_text.pack()

# Add buttons for text formatting
bold_button = tk.Button(root, text="Bold", command=toggle_bold)
bold_button.pack(side=tk.LEFT, padx=10)

italic_button = tk.Button(root, text="Italic", command=toggle_italic)
italic_button.pack(side=tk.LEFT, padx=10)

underline_button = tk.Button(root, text="Underline", command=toggle_underline)
underline_button.pack(side=tk.LEFT, padx=10)

# Add button to select files
media_files = []  # List to store selected media files
select_button = tk.Button(root, text="Select Media Files", command=select_files)
select_button.pack()

media_label = tk.Label(root, text="No files selected")
media_label.pack()

send_button = tk.Button(root, text="Send Emails", command=send_email)
send_button.pack()

# Text widget for message body with tag configurations for bold, italic, and underline
text_widget = message_text
text_widget.tag_configure("bold", font=("Helvetica", 12, "bold"))
text_widget.tag_configure("italic", font=("Helvetica", 12, "italic"))
text_widget.tag_configure("underline", font=("Helvetica", 12, "underline"))
text_widget.tag_configure("current_style", font=("Helvetica", 12))

# Initial states of formatting options
bold = False
italic = False
underline = False

root.mainloop()
