import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedStyle
import threading
import speech_recognition as sr
import pyttsx3
import mysql.connector

# Database Connection Class
class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@sanu111",
            database="SpeechRecognitionDB"
        )
        self.cursor = self.conn.cursor()

    def insert_data(self, input_text, recognized_text, language):
        query = "INSERT INTO SpeechResults (input_text, recognized_text, language) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (input_text, recognized_text, language))
        self.conn.commit()

    def fetch_data(self):
        self.cursor.execute("SELECT * FROM SpeechResults")
        return self.cursor.fetchall()

    def delete_record(self, record_id):
        query = "DELETE FROM SpeechResults WHERE id = %s"
        self.cursor.execute(query, (record_id,))
        self.conn.commit()

    def reset_auto_increment(self):
        self.cursor.execute("SET @new_id = 0;")
        self.cursor.execute("UPDATE SpeechResults SET id = (@new_id := @new_id + 1);")
        self.cursor.execute("ALTER TABLE SpeechResults AUTO_INCREMENT = 1;")
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

# Main Application Class
class SpeechRecognitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech Recognition System")
        self.geometry("650x450")
        
        # Apply Themed Style
        self.style = ThemedStyle(self)
        self.style.set_theme("radiance")  # A stylish dark theme
        self.style.configure('.', background='#FFB6C1')
        #self.configure(bg="#FFD1DC")  # Background Color
        self.switch_frame(HomePage)

    def switch_frame(self, frame_class):
        for widget in self.winfo_children():
            widget.destroy()
        frame_class(self).pack(expand=True, fill="both")

# Home Page
class HomePage(ttk.Frame):

    
    def __init__(self, master):
        super().__init__(master, style="TFrame")
        ttk.Label(self, text="Speech Recognition System", font=("Cambria", 25 , "bold"), foreground="black", background="#FFB6C1").pack(pady=20)

        btn_style = {"padding": 10, "width": 25}  # Button Style
        
        ttk.Button(self, text="Text to Speech", **btn_style, command=lambda: master.switch_frame(TextToSpeechPage)).pack(pady=10)
        ttk.Button(self, text="Speech to Text", **btn_style, command=lambda: master.switch_frame(SpeechToTextPage)).pack(pady=10)
        ttk.Button(self, text="Real-Time Speech", **btn_style, command=lambda: master.switch_frame(RealTimePage)).pack(pady=10)
        ttk.Button(self, text="View Saved Results", **btn_style, command=lambda: master.switch_frame(ViewResultsPage)).pack(pady=10)

# Text to Speech Page
class TextToSpeechPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Enter Text:", font=("Arial", 14, "bold"), foreground="white", background="#FFB6C1").pack(pady=10)

        self.text_entry = ttk.Entry(self, width=50)
        self.text_entry.pack(pady=10)

        ttk.Button(self, text="Play", command=self.convert_to_speech).pack(pady=10)
        ttk.Button(self, text="Download Audio", command=self.save_speech_to_file).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: master.switch_frame(HomePage)).pack(pady=10)

    def convert_to_speech(self):
        text = self.text_entry.get()
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def save_speech_to_file(self):
        text = self.text_entry.get()
        if text.strip():
            engine = pyttsx3.init()
            file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")])
            if file_path:
                engine.save_to_file(text, file_path)
                engine.runAndWait()
                messagebox.showinfo("Success", f"Audio saved successfully at {file_path}")
        else:
            messagebox.showerror("Error", "Please enter text to convert.")

# Speech to Text Page
class SpeechToTextPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.db = Database()

        ttk.Label(self, text="Select an Audio File", font=("Arial", 14, "bold"), foreground="white", background="#FFB6C1").pack(pady=10)

        self.file_path_label = ttk.Label(self, text="No file selected", background="#FFB6C1", foreground="black")
        self.file_path_label.pack(pady=5)

        ttk.Button(self, text="Select File", command=self.select_audio_file).pack(pady=10)
        ttk.Button(self, text="Convert & Save", command=self.save_text).pack(pady=10)

        self.text_output = tk.Text(self, height=10, width=50, bg="white", fg="black", font=("Arial", 12))
        self.text_output.pack(pady=10)

        ttk.Button(self, text="Back", command=lambda: master.switch_frame(HomePage)).pack(pady=10)

    
def select_audio_file(self):
    file_path = filedialog.askopenfilename(
        title="Select an audio file",
        filetypes=[
            ("Supported audio files", "*.wav *.aiff *.aif *.flac"),
        ],
    )

    if not file_path:
        return

    supported_extensions = {".wav", ".aiff", ".aif", ".flac"}
    extension = os.path.splitext(file_path)[1].lower()

    if extension not in supported_extensions:
        messagebox.showerror(
            "Unsupported Audio Format",
            "Please select a WAV, AIFF, AIF, or FLAC file.",
        )
        return

    self.file_path = file_path
    self.label.config(text=f"Selected: {os.path.basename(file_path)}")


    def save_text(self):
        if hasattr(self, 'file_path'):
            threading.Thread(target=self.process_audio).start()

    def process_audio(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.file_path) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

            self.text_output.delete('1.0', tk.END)
            self.text_output.insert(tk.END, text)

            # Save to Database
            self.db.insert_data(self.file_path, text, "ENGLISH")
            messagebox.showinfo("Success", "Text saved to database.")

        except sr.UnknownValueError:
            messagebox.showerror("Error", "Speech not recognized.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Google Speech API error: {e}")

# View Saved Results Page
class ViewResultsPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.db = Database()

        ttk.Label(self, text="Stored Speech Results", font=("Arial", 18, "bold"), foreground="black", background="#FFB6C1").pack(pady=10)
        
        columns = ("ID", "Input Text", "Recognized Text", "Language", "Timestamp")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Recognized Text":
                self.tree.column(col, width=300, anchor="w")  # Increase width for full output
            else:
                self.tree.column(col, width=120, anchor="center")
        
        self.tree.pack(pady=10, expand=True, fill="both")
        self.tree.bind("<Double-1>", self.show_full_text)  # Bind double-click event
        self.load_results()
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected_record).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Back", command=lambda: master.switch_frame(HomePage)).pack(side="left", padx=10)

    def load_results(self):
        records = self.db.fetch_data()
        for row in records:
            self.tree.insert("", "end", values=row)

    def show_full_text(self, event):
        """ Display full Recognized Text when a row is double-clicked """
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if len(item_values) > 2:
                full_text = item_values[2]  # Recognized Text column
                messagebox.showinfo("Recognized Text", full_text)
    
    def delete_selected_record(self):
        """ Delete the selected record from the database and update the treeview """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return

        item_values = self.tree.item(selected_item, "values")
        record_id = item_values[0]  # ID column
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            self.db.delete_record(record_id)
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Record deleted successfully.")
            
            # Refresh the TreeView
            self.refresh_results()
            
           
    
    def refresh_results(self):
        """ Reload the TreeView with updated results """
        for row in self.tree.get_children():
            self.tree.delete(row)  # Clear existing entries
        self.load_results() 
        self.db.reset_auto_increment() # Reload data from database

# Real-Time Speech Recognition Page
class RealTimePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.db = Database()
        self.stop_event = threading.Event()

        ttk.Label(self, text="Real-Time Speech Recognition", font=("Arial", 18, "bold"), foreground="white", background="#FFB6C1").pack(pady=10)

        self.language_var = tk.StringVar(value="ENGLISH")  # Default language is English
        ttk.Label(self, text="Select Language:", font=("Arial", 12), background="#FFB6C1").pack(pady=5)
        self.language_menu = ttk.Combobox(self, textvariable=self.language_var, values=["ENGLISH", "HINDI", "MARATHI"], state="readonly")
        self.language_menu.pack(pady=5)
        self.language_menu.set("ENGLISH")

        self.text_box = tk.Text(self, height=10, width=50, bg="white", fg="black", font=("Arial", 12))
        self.text_box.pack(pady=10)

        ttk.Button(self, text="Start", command=self.start_real_time_recognition).pack(pady=10)
        ttk.Button(self, text="Stop", command=self.stop_real_time_recognition).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: master.switch_frame(HomePage)).pack(pady=10)

    def start_real_time_recognition(self):
        self.text_box.delete('1.0', tk.END)
        threading.Thread(target=self.listen_microphone).start()

    def stop_real_time_recognition(self):
        self.stop_event.set()

    def listen_microphone(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.text_box.insert(tk.END, "Listening...\n")
            while not self.stop_event.is_set():
                try:
                    audio = self.recognizer.listen(source)
                    language_code = self.language_var.get()
                    text = self.recognizer.recognize_google(audio, language=language_code)
                    self.text_box.insert(tk.END, text + "\n")
                    self.db.insert_data("Real-Time Speech", text, language_code)
                except sr.UnknownValueError:
                    self.text_box.insert(tk.END, "Could not understand audio.\n")
                except sr.RequestError as e:
                    self.text_box.insert(tk.END, f"API request error: {e}\n")

if __name__ == "__main__":
    app = SpeechRecognitionApp()
    app.mainloop()


