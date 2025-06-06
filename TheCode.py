import tkinter as tk
from tkinter import messagebox
import json
import os
import threading
import pyautogui
import pyperclip
import time
import random
import string

CONFIG_FILE = "config.json"

def default_config():
    return {
        "woord_begin": [253, 455],
        "woord_eind": [1205, 486],
        "input_field": [738, 560],
        "woordenlijst": {
            "uit": "aus",
            "bij": "bei",
            "mit": "met",
            "nach": "na",
            "seit": "sinds",
            "von": "van",
            "zu": "naar"
        }
    }

class BotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bot + Config Editor")
        self.geometry("700x700")

        self.config_data = self.load_config()
        self.bot_running = False
        self.bot_thread = None

        # Coördinaten invoer
        self.entries = {}
        for coord_name in ["woord_begin", "woord_eind", "input_field"]:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            tk.Label(frame, text=f"{coord_name} (x, y):").pack(side="left")
            entry_x = tk.Entry(frame, width=8)
            entry_x.pack(side="left", padx=5)
            entry_y = tk.Entry(frame, width=8)
            entry_y.pack(side="left", padx=5)
            self.entries[coord_name] = (entry_x, entry_y)

        # Woordenlijst
        tk.Label(self, text="Woordenlijst (taal : Nederlands):").pack(pady=(20, 5))
        self.woordlijst_text = tk.Text(self, height=20, width=80)
        self.woordlijst_text.pack()

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        self.btn_save = tk.Button(btn_frame, text="Opslaan Config", command=self.save_config)
        self.btn_save.pack(side="left", padx=10)

        self.btn_start = tk.Button(btn_frame, text="Start Bot", command=self.toggle_bot)
        self.btn_start.pack(side="left", padx=10)

        self.load_into_widgets()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            return default_config()

    def load_into_widgets(self):
        for key in ["woord_begin", "woord_eind", "input_field"]:
            x_entry, y_entry = self.entries[key]
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            x_entry.insert(0, str(self.config_data.get(key, [0, 0])[0]))
            y_entry.insert(0, str(self.config_data.get(key, [0, 0])[1]))

        self.woordlijst_text.delete(1.0, tk.END)
        woordenlijst = self.config_data.get("woordenlijst", {})
        for k, v in woordenlijst.items():
            self.woordlijst_text.insert(tk.END, f"{k} : {v}\n")

    def save_config(self):
        try:
            for key in ["woord_begin", "woord_eind", "input_field"]:
                x_entry, y_entry = self.entries[key]
                x = int(x_entry.get())
                y = int(y_entry.get())
                self.config_data[key] = [x, y]
        except ValueError:
            messagebox.showerror("Fout", "Coördinaten moeten gehele getallen zijn!")
            return

        tekst = self.woordlijst_text.get(1.0, tk.END).strip()
        woordenlijst = {}
        for line in tekst.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                woordenlijst[k.strip()] = v.strip()
        self.config_data["woordenlijst"] = woordenlijst

        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=4)

        messagebox.showinfo("Succes", "Configuratie opgeslagen!")

    def toggle_bot(self):
        if self.bot_running:
            self.bot_running = False
            self.btn_start.config(text="Start Bot")
        else:
            # Save config voordat je start
            self.save_config()
            self.bot_running = True
            self.btn_start.config(text="Stop Bot")
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

    def maak_typfout(self, woord):
        if len(woord) < 3:
            return woord
        i = random.randint(0, len(woord)-1)
        fout = list(woord)
        fout[i] = random.choice(string.ascii_lowercase)
        return ''.join(fout)

    def geef_antwoord(self, een_woord):
        woordenlijst = self.config_data.get("woordenlijst", {})
        juist = woordenlijst.get(een_woord, "")
        return juist if random.random() < 0.8 else self.maak_typfout(juist)

    def menselijk_typen(self, tekst):
        for letter in tekst:
            pyautogui.write(letter)
            time.sleep(random.uniform(0.08, 0.25))

    def run_bot(self):
        # Lees coördinaten opnieuw in bij starten, voor veiligheid
        try:
            with open(CONFIG_FILE, "r") as f:
                self.config_data = json.load(f)
        except Exception as e:
            print("Fout bij inladen config:", e)
            self.bot_running = False
            self.btn_start.config(text="Start Bot")
            return

        woord_begin = tuple(self.config_data.get("woord_begin", (0, 0)))
        woord_eind = tuple(self.config_data.get("woord_eind", (0, 0)))
        input_field = tuple(self.config_data.get("input_field", (0, 0)))
        woordenlijst = self.config_data.get("woordenlijst", {})

        print("Bot gestart. Druk Ctrl+C in terminal of klik Stop Bot om te stoppen.")
        time.sleep(3)

        while self.bot_running:
            # Selecteer tekst via drag
            pyautogui.moveTo(woord_begin, duration=0.2)
            pyautogui.mouseDown()
            time.sleep(0.2)
            pyautogui.moveTo(woord_eind, duration=0.4)
            pyautogui.mouseUp()

            time.sleep(0.3)
            # Kopieer met Cmd+C of Ctrl+C (check OS)
            if os.name == "posix":  # Mac/Linux
                pyautogui.hotkey('command', 'c')
            else:
                pyautogui.hotkey('ctrl', 'c')

            time.sleep(0.3)
            tekst = pyperclip.paste().strip().lower()

            if tekst not in woordenlijst:
                print(f" '{tekst}' niet gevonden.")
                time.sleep(2)
                continue

            antwoord = self.geef_antwoord(tekst)
            wachttijd = random.uniform(1.0, 5.0)
            print(f" '{tekst}' → '{antwoord}' (na {wachttijd:.2f}s)")
            time.sleep(wachttijd)

            # Ga naar input field en typ
            pyautogui.moveTo(input_field, duration=0.2)
            pyautogui.click()
            self.menselijk_typen(antwoord)
            pyautogui.press('enter')

            time.sleep(2.5)

        print("Bot gestopt.")

if __name__ == "__main__":
    app = BotApp()
    app.mainloop()
