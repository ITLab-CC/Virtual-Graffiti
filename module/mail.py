import os
import shutil
from module.config import Config
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime

class Mail:
    def __init__(self):
        return

    def set_conf():
        root = tk.Tk()
        root.withdraw()
        while True:
            result = simpledialog.askstring("Input", "Enter the email which you want to use for sending:", parent=root)
            if result is None:
                break
            globals.CONF.EMAIL_SENDER = result
            break
        while True:
            result = simpledialog.askstring("Input", "Enter the password for this email:", parent=root)
            if result is None:
                break
            self.CONF.EMAIL_PASSWORD = result
            break
        while True:
            result = simpledialog.askstring("Input", "Enter the smtp-server for this email:", parent=root)
            if result is None:
                break
            self.CONF.EMAIL_SMTP_SERVER = result
            break
        root.destroy()
        self.SaveToJSON()

    def send_mail(self, mail_enable, sender_email, password, smtp_server, path_from_file):
        if mail_enable:
            # get data
            files = os.listdir(path_from_file)
            if len(files) > 0 and "tmp" not in str(files):
                save_folder = "./sendet_mails"
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)

                print("sending mail...")

                file_name = str(files[0])
                receiver_email = Path(path_from_file + "/" + file_name).stem

                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = Path(path_from_file + "/" + file_name).stem
                message["Subject"] = "Virutalles Graffiti"

                body = "Dein gezeichtnes Graffiti. Nacht der Ausbildung, 10 März 2023 bei Entega"
                message.attach(MIMEText(body, "plain"))

                with open(path_from_file + "/" + file_name, "rb") as file:
                    attachment = MIMEApplication(file.read(), _subtype="txt")
                    attachment.add_header("Content-Disposition", "attachment", filename="Graffiti.png")
                    message.attach(attachment)

                with smtplib.SMTP(smtp_server, 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    text = message.as_string()
                    server.sendmail(sender_email, receiver_email, text)

                now = datetime.now()
                shutil.move(path_from_file + "/" + file_name , save_folder)
                os.rename(save_folder  + "/" + file_name, save_folder  + "/" + receiver_email + str(now.strftime("-%H-%M-%S")) + ".png")
                print("mail sendet and file moved")