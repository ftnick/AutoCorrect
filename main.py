LocalVersion = "PublicRelease1.4"

import requests
import os
import configparser
from pymsgbox import *
from io import BytesIO
from PIL import ImageTk
from PIL import Image
from print_color import print
import tkinter as tk
import time
from print_color import print
from googletrans import Translator, LANGUAGES
from fetch_module import Download


print("Awaiting...", tag='IDLE', tag_color='cyan')

def exit(type):
    alert(text='Script Error', title='ERR', button='OK')
    sys.exit(1)
    
config_url = Download("https://raw.githubusercontent.com/ftnick/AutoCorrect/main/config.ini", ".ini")

def GetConfig(section, setting):
    try:
        response = requests.get(config_url)
        response.raise_for_status()

        config = configparser.ConfigParser()
        config.read_string(response.text)

        value = config.get(section, setting)
        return value
    except requests.RequestException as e:
        print(f"Error fetching config file: {e}", tag="GetConfig()", tag_color='yellow')
        return
    except configparser.Error as e:
        print(f"Error parsing config file: {e}", tag="GetConfig()", tag_color='yellow')
        return
    
SyncCheck = GetConfig("Info", "Version")
if SyncCheck != LocalVersion and SyncCheck:
    alert(text="Your script version is currently unsynchronized. This is likely an error on our end. Please allow a few minutes for all scripts to synchronize with the website. We apologize for any inconvenience.", title='ERROR_SYNC', button='OK')
    print("DeSynced From CONFIG", tag='VERSIONSYNC', tag_color='red')
    sys.exit(1)
else:
    print(f"Confirmed Version Sync ({SyncCheck})", tag='VERSIONSYNC', tag_color='green')

    
ShutdownCheck = GetConfig("Communication", "Shutdown")
if ShutdownCheck != "No" and ShutdownCheck:
    alert(text='Attention users: This application is currently undergoing maintenance and will be back up soon. We apologize for any inconvenience. Thank you for your understanding.', title='Temporary Shutdown', button='OK')
    print("Shutdown Requested From CONFIG", tag='SHUTDOWN', tag_color='red')
    sys.exit(1)
else:
    print(f"Confirmed No Shutdown ({ShutdownCheck})", tag='SHUTDOWN', tag_color='green')

WarningCheck = GetConfig("Communication", "Warning")
if WarningCheck != "None" and WarningCheck:
    alert(text=str(WarningCheck), title='WARNING', button='OK')
    print("Warning Requested From CONFIG", tag='WARNING', tag_color='yellow')
else:
    print(f"Confirmed No Warning ({WarningCheck})", tag='WARNING', tag_color='green')

NoticeCheck = GetConfig("Communication", "Notice")
if NoticeCheck != "None" and NoticeCheck:
    alert(text=str(NoticeCheck), title='Notice', button='OK')
    print("Notice Requested From CONFIG", tag='NOTICE', tag_color='yellow')
else:
    print(f"Confirmed No Notice ({NoticeCheck})", tag='NOTICE', tag_color='green')


class AutoCorrectGUI:
    def __init__(self, master):
        self.master = master
        SetTitle = GetConfig("Info","Title")
        if SetTitle:
            self.master.title(str(SetTitle))
        else:
            print("FAILED TO FIND TITLE FROM CONFIG, FALLING BACK TO DEFAULT", tag='ERROR', tag_color='red')
            self.master.title("Auto-Correct")
        self.master.attributes('-topmost', True)
        self.master.resizable(False, False)

        # Main frame
        self.main_frame = tk.Frame(master, bg="#E1D8B9")
        self.main_frame.pack(padx=10, pady=10)

        # Input label and text
        self.input_label = tk.Label(self.main_frame, text="Enter Text:", bg="#E1D8B9")
        self.input_label.grid(row=0, column=0, pady=(0, 5), sticky="w")

        self.input_text = tk.Text(self.main_frame, height=5, width=40, wrap=tk.WORD, bg="#F4F1DE")
        self.input_text.grid(row=1, column=0, pady=(0, 10))

        # Output label and text
        self.output_label = tk.Label(self.main_frame, text="Auto-Corrected Text:", bg="#E1D8B9")
        self.output_label.grid(row=2, column=0, pady=(0, 5), sticky="w")

        self.output_text = tk.Text(self.main_frame, height=5, width=40, state=tk.DISABLED, wrap=tk.WORD, bg="#F4F1DE")
        self.output_text.grid(row=3, column=0, pady=(0, 10))

        # Status label and text
        self.status_label = tk.Label(self.main_frame, text="Status:", bg="#E1D8B9")
        self.status_label.grid(row=4, column=0, pady=(0, 5), sticky="w")

        self.status_text = tk.Text(self.main_frame, height=1, width=40, state=tk.DISABLED, bg="#F4F1DE", wrap=tk.WORD)
        self.status_text.grid(row=5, column=0, pady=(0, 10))

        # Auto-Correct button
        self.correct_button = tk.Button(self.main_frame, text="Auto-Correct", command=self.auto_correct, bg="#BFB48F")
        self.correct_button.grid(row=6, column=0, pady=(10, 0))
        
        SetVersion = GetConfig("Info","Version")
        if SetVersion:
            SetVersion = str(SetVersion)
            info_text = f"Auto-Correction can fail and might make mistakes. (Version: {SetVersion})"
        else:
            print("FAILED TO FIND VERSION FROM CONFIG", tag='ERROR', tag_color='red')
            info_text = "Auto-Correction can fail and might make mistakes. (Version: ErrorNotFound)"

        self.info_label = tk.Label(self.main_frame, text=info_text, bg="#E1D8B9", fg="red")
        self.info_label.grid(row=7, column=0, pady=(10, 0), sticky="w")

    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, message)
        self.status_text.config(state=tk.DISABLED)
        self.adjust_status_text_height()

    def adjust_status_text_height(self):
        status_lines = int(self.status_text.index(tk.END).split('.')[0])
        self.status_text.config(height=max(1, status_lines))

    def auto_correct(self):
        original_text = self.input_text.get("1.0", tk.END).strip()

        if len(original_text) > 100:
            Characterp = len(original_text)
            self.update_status(f"TERMINATED: CANNOT PASS 100 CHARACTERS ({Characterp}/100)")
            print(f"CANNOT PASS 100 CHARACTERS ({Characterp}/100)", tag='TERMINATED', tag_color='red')
            return
        
        if len(original_text) == 0:
            Characterp = len(original_text)
            self.update_status(f"TERMINATED: CHARACTER LIMIT FAILED, OR NO CHARACTERS DETECTED ({Characterp}/100)")
            print(f"CHARACTER LIMIT FAILED, OR NO CHARACTERS DETECTED ({Characterp}/100)", tag='TERMINATED', tag_color='red')
            return

        try:
            # Use Google Translate for auto-correction
            translator = Translator()
            self.update_status("Correcting...")
            corrected_text = translator.translate(original_text, dest='en').text
            self.update_status("Auto-correction complete.")
        except Exception as e:
            print(f"Error during Correction: {e}", tag='ERROR', tag_color='red')
            corrected_text = "Correction Error"
            self.update_status("Error during auto-correction.")

        # Update the output text
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, corrected_text)

        # Underline words that have changed
        self.underline_changed_words(original_text, corrected_text)

        self.output_text.config(state=tk.DISABLED)

    def underline_changed_words(self, original_text, corrected_text):
        # Define a tag for underlining
        self.output_text.tag_configure("underline", underline=True)

        # Split the original and corrected text into words
        original_words = original_text.split()
        corrected_words = corrected_text.split()

        for orig_word, corrected_word in zip(original_words, corrected_words):
            self.update_status(f"Checking: ({orig_word.lower()}) Compared to: ({corrected_word.lower()})")
            print(f"Checking: ({orig_word.lower()}) Compared to: ({corrected_word.lower()})", tag='COMPARING', tag_color='yellow')
            # Check if the word has changed
            if orig_word.lower() != corrected_word.lower():
                # Get the index of the corrected word in the Text widget
                start_index = corrected_text.index(corrected_word)
                end_index = start_index + len(corrected_word)
                self.update_status(f"Corrected: ({corrected_word})")
                print(f"Corrected: ({corrected_word})", tag='CORRECTION', tag_color='purple')
                # Add the "underline" tag to the changed word
                self.output_text.tag_add("underline", f"1.{start_index}", f"1.{end_index}")
        time.sleep(0.5)
        
        self.update_status("Finished")
        print("Finished", tag='SUCCESS', tag_color='blue')

if __name__ == "__main__":
    print("Registering Root", tag='SUCCESS', tag_color='green')
    root = tk.Tk()
  
    icon_url = GetConfig("FileURLS", "IconFile")

    IconImage = Download(icon_url, ".ico")
    try:
        response = requests.get(IconImage)
        response.raise_for_status()
        icon_data = BytesIO(response.content)
        icon = Image.open(icon_data)
        icon_photo = ImageTk.PhotoImage(icon)
        root.iconphoto(True, icon_photo)
    except requests.exceptions.RequestException as e:
        print(f"Icon Fail: {e}", tag='ICON_FATAL_ERROR', background="red", color="magenta", tag_color='magenta')
        sys.exit(1)

    print("Registering App", tag='SUCCESS', tag_color='green')
    app = AutoCorrectGUI(root)
    print("Registering mainloop", tag='SUCCESS', tag_color='green')
    root.mainloop()
