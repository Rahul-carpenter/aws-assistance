import tkinter as tk
from tkinter import messagebox, Toplevel, simpledialog
import os
import boto3
import uuid
import pywhatkit
import speech_recognition as sr
import datetime as dt
import cv2
import time
from instabot import Bot

# Initialize AWS clients
myec2 = boto3.client("ec2")
s3_client = boto3.client('s3')

# Global variables
voice_assistance_button = None

def create_basic_window():
    global voice_assistance_button
    root = tk.Tk()
    root.title("Feature-Controlled Assistant")
    root.geometry("450x700")
    root.configure(bg="#333333")
    
    header_label = tk.Label(root, text="Feature-Controlled Assistant", font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg="#333333")
    header_label.pack(pady=20)

    date = dt.datetime.now()
    date_label = tk.Label(root, text="Date: %s" % date.strftime("%Y-%m-%d %H:%M:%S"), fg="#FFFFFF", bg="#333333")
    date_label.pack(pady=5)

    voice_assistance_button = tk.Button(root, text="Voice Assistance", command=enable_voice_assistance, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
    voice_assistance_button.pack(pady=15)
    voice_assistance_button.bind("<Enter>", lambda e: voice_assistance_button.config(bg="#45A049"))
    voice_assistance_button.bind("<Leave>", lambda e: voice_assistance_button.config(bg="#4CAF50"))

    features = [
        ("Send Email", send_email),
        ("Create EC2 Instance", on_button_ec2),
        ("Create S3 Bucket", s3_bucket_create),
        ("Open Notepad", on_button_click),
        ("Open Chrome", on_click),
        ("Open Paint", on_click_paint),
        ("Open Word", on_click_word),
        ("Play on YouTube", youtube_music),
        ("Take Photo", take_photo)
    ]

    for feature_text, command in features:
        button = tk.Button(root, text=feature_text, command=command, width=25, bg="#008CBA", fg="white", font=("Helvetica", 10, "bold"))
        button.pack(pady=8)
        button.bind("<Enter>", lambda e, b=button: b.config(bg="#007BB5"))
        button.bind("<Leave>", lambda e, b=button: b.config(bg="#008CBA"))

    exit_button = tk.Button(root, text="Exit", width=15, fg="white", bg="#f44336", font=("Helvetica", 10, "bold"), command=root.destroy)
    exit_button.pack(pady=15)
    exit_button.bind("<Enter>", lambda e: exit_button.config(bg="#E57373"))
    exit_button.bind("<Leave>", lambda e: exit_button.config(bg="#f44336"))
    root.mainloop()

def open_custom_input_dialog(title, prompt, on_submit):
    input_window = Toplevel()
    input_window.title(title)
    input_window.geometry("400x200")
    input_window.configure(bg="#444444")
    
    title_label = tk.Label(input_window, text=title, font=("Helvetica", 16, "bold"), fg="#FFFFFF", bg="#444444")
    title_label.pack(pady=10)

    prompt_label = tk.Label(input_window, text=prompt, font=("Helvetica", 12), fg="#CCCCCC", bg="#444444")
    prompt_label.pack(pady=5)

    entry_var = tk.StringVar()
    entry_box = tk.Entry(input_window, textvariable=entry_var, font=("Helvetica", 12), width=30)
    entry_box.pack(pady=10)
    entry_box.focus()

    submit_button = tk.Button(input_window, text="Submit", command=lambda: [on_submit(entry_var.get()), input_window.destroy()], bg="#008CBA", fg="white", font=("Helvetica", 10, "bold"))
    submit_button.pack(pady=10)

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Voice Assistance", "Listening for voice input...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        user_input = recognizer.recognize_google(audio)
        return user_input
    except sr.UnknownValueError:
        messagebox.showwarning("Voice Assistance", "Sorry, I could not understand your voice.")
        return None
    except sr.RequestError:
        messagebox.showerror("Voice Assistance", "There was a problem with the speech recognition service.")
        return None

def enable_voice_assistance():
    global voice_assistance_button
    voice_assistance_button.config(state=tk.DISABLED)
    user_input = get_voice_input()
    if user_input:
        process_voice_command(user_input)
    voice_assistance_button.config(state=tk.ACTIVE)

def process_voice_command(command):
    if "email" in command:
        send_email()
    elif "EC2" in command:
        on_button_ec2()
    elif "notepad" in command:
        on_button_click()
    elif "chrome" in command:
        on_click()
    elif "paint" in command:
        on_click_paint()
    elif "word" in command:
        on_click_word()
    elif "play on YouTube" in command:
        youtube_music()
    else:
        messagebox.showinfo("Info", "Command not recognized.")

def send_email():
    msg = get_voice_input()  # Voice input for message
    recipient_email = simpledialog.askstring("Email Input", "Enter recipient's email address:")
    
    if recipient_email and msg:
        try:
            pywhatkit.send_mail("testprect@gmail.com", "aljeobaueiacqtko", "Test Code", msg, recipient_email)
            messagebox.showinfo("Success", f"Email sent to {recipient_email}!")
        except Exception as e:
            messagebox.showerror("Error", f"Error sending email: {str(e)}")
    elif not recipient_email:
        messagebox.showwarning("Missing Email", "Please provide a recipient email address.")
    elif not msg:
        messagebox.showwarning("Missing Message", "No message provided. Please speak your message.")

def on_button_ec2():
    instance_info = create_ec2_instance()
    if instance_info:
        messagebox.showinfo("Success", f"EC2 instance created successfully!\nInstance ID: {instance_info['InstanceId']}")
    else:
        messagebox.showerror("Error", "Failed to create EC2 instance.")

def create_ec2_instance():
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.run_instances(
            ImageId='ami-0a0f1259dd1c90938',
            InstanceType='t2.micro',
            MaxCount=1,
            MinCount=1
        )
        if 'Instances' in response and len(response['Instances']) > 0:
            return response['Instances'][0]
        else:
            return None
    except Exception as e:
        messagebox.showerror("Error", f"Error creating EC2 instance: {str(e)}")
        return None

def on_button_click():
    os.system("notepad")

def on_click():
    os.system("start chrome")

def on_click_paint():
    os.system("start mspaint")

def on_click_word():
    os.system("start winword")

def s3_bucket_create():
    bucket_name = f"my-bucket-{uuid.uuid4()}"
    try:
        s3_client.create_bucket(
            ACL='private',
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'}
        )
        messagebox.showinfo("Success", f"S3 bucket '{bucket_name}' created.")
    except Exception as e:
        messagebox.showerror("Error", f"Error creating S3 bucket: {str(e)}")

def youtube_music():
    song_name = get_voice_input()
    if song_name:
        pywhatkit.playonyt(song_name)
    else:
        messagebox.showwarning("Input Error", "No song name provided.")

def take_photo():
    cap = cv2.VideoCapture(0)
    time.sleep(1)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('photo.jpg', frame)
        messagebox.showinfo("Photo", "Photo captured and saved as 'photo.jpg'.")
        cap.release()
        cv2.destroyAllWindows()
    else:
        messagebox.showerror("Error", "Failed to capture photo.")

# Run the GUI
create_basic_window()
