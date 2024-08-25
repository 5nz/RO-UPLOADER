""" ERM THE SIGMA DONT CHANGE ANYTHING BELOW IF YOU DONT KNOW WHAT YOUR DOING PLEASE AND THANKS AND BYE! join the discord server discord.gg/4wffQmV6mR"""

import sounddevice as sd
from scipy.io.wavfile import read
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from tkinter import ttk, PhotoImage
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk
import io
import random
import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Uploader:
    def __init__(self, config_file=resource_path("./Data/config.json")):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
            
    def load_user_info(self):
        user_info_file = resource_path("./Data/user_info.json")
        try:
            with open(user_info_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None    
    
    def save_user_info(self, user_info):
        userINFOFILE = resource_path("./Data/user_info.json")
        with open(userINFOFILE, "w") as f:
            json.dump(user_info, f, indent=4)

    def get_csrf_token(self):
        url = "https://auth.roblox.com/v2/logout"
        headers = {
            "Cookie": f".ROBLOSECURITY={self.config.get('cookie')}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, headers=headers)
        csrf_token = response.headers.get("X-CSRF-TOKEN")
        if csrf_token:
            return csrf_token
        else:
            raise ValueError("CSRF token not found")

    def get_user_info(self):
        url = "https://users.roblox.com/v1/users/authenticated"
        headers = {
            "Cookie": f".ROBLOSECURITY={self.config.get('cookie')}",
            "User-Agent": "Roblox/WinInet"
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            user_info = res.json()
            return user_info
        else:
            return None

    def create_api_key(self):
        xsrf_token = self.get_csrf_token()
        user_info = self.get_user_info()
        if user_info is None:
            return None
        payload = {
            "cloudAuthUserConfiguredProperties": {
                "name": "RO-UPLOADER",
                "description": "[ API KEY WAS CREATED USING RO-UPLOADER ]",
                "isEnabled": True,
                "allowedCidrs": ["0.0.0.0/0"],
                "scopes": [
                    {
                        "scopeType": "asset",
                        "targetParts": ["U"],
                        "operations": ["read", "write"]
                    }
                ]
            }
        }
        headers = {
            "Cookie": f".ROBLOSECURITY={self.config.get('cookie')}",
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": xsrf_token
        }
        
        res = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers)
        
        if res.status_code == 200:
            try:
                api_key_info = res.json()
                self.config['api_key'] = api_key_info["apikeySecret"]
                self.save_config()
                return api_key_info["apikeySecret"]
            except json.JSONDecodeError:
                return "Error decoding JSON response: " + res.text
        else:
            return f"Error: {res.status_code} - {res.text}"

    def start_upload(self, img_data):
        url = "https://apis.roblox.com/assets/v1/assets"
        headers = {
            "x-api-key": self.config.get('api_key'),
            "Content-Type": "application/json",
        }
        user_info = self.load_user_info()
        if user_info is None:
            return "Failed to get user info."

        with io.BytesIO(img_data) as file:
            form = MultipartEncoder(
                fields={
                    "fileContent": ("asset.png", file, "image/png"),
                    "request": json.dumps({
                        "assetType": "Decal",
                        "displayName": "RO-UPLOADER",
                        "description": "[ RO-UPLOADER || BY 5NZ ]",
                        "creationContext": {
                            "creator": {
                                "userId": user_info["userID"]
                            }
                        }
                    })
                }
            )
            headers["Content-Type"] = form.content_type
            res = requests.post(url, data=form, headers=headers)

        if res.status_code == 200:
            return "Asset uploaded successfully!"
        else:
            return f"Error: {res.status_code} - {res.text}"

def process_image(file_path):
    with Image.open(file_path) as image:
        max_size = 420
        width, height = image.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            width = int(width * ratio)
            height = int(height * ratio)
            image = image.resize((width, height), Image.LANCZOS)

        unique_identifier = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), unique_identifier, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = random.randint(0, width - text_width)
        y = random.randint(0, height - text_height)

        draw.text((x, y), unique_identifier, font=font, fill=(255, 255, 255))

        num_pixels_to_change = 5
        for _ in range(num_pixels_to_change):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            pixel = image.getpixel((x, y))
            new_pixel = tuple((color + random.randint(0, 10)) % 256 for color in pixel)
            image.putpixel((x, y), new_pixel)

        output = io.BytesIO()
        image.save(output, format='PNG')
        output.seek(0)
        return output.read()


class ROUPLOADERUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RO-UPLOADER || BY 5NZ")
        img = PhotoImage(file=resource_path('./Data/Icons/ro_uploader-5.png'))
        root.iconphoto(False, img)
        self.root.config(bg="#26242f")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#26242f')
        self.style.configure('TButton', background='#4a4a4a', foreground='white', padding=[10, 5])
        self.style.configure('TEntry', padding=[10, 5], relief='flat')
        self.style.configure('TLabel', background='#26242f', foreground='white')
        
        
        self.roblox = Uploader()

        self.tab_control = ttk.Notebook(root)
        
        self.create_api_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.create_api_tab, text='Create API')
        
        self.cookie_label = tk.Label(self.create_api_tab, text="Roblox Cookie:")
        self.cookie_label.pack(pady=(10, 5))
        self.cookie_entry = ttk.Entry(self.create_api_tab)
        self.cookie_entry.pack(pady=(0, 10))

        self.create_api_button = ttk.Button(self.create_api_tab, text="Create API Key", command=self.create_api_key)
        
        self.note_label = ttk.Label(self.create_api_tab, text="Note: If you already created 1 API key on the account you dont have to recreate it, You recreate when you get banned!", style='TLabel', font=('Helvetica', 10))
        self.note_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.create_api_button.pack(pady=10)
        

        self.main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text='Main')

        self.filepath_label = ttk.Label(self.main_tab, text="Asset File Path:")
        self.filepath_label.pack(pady=(10, 5))
        self.filepath_entry = ttk.Entry(self.main_tab, state="readonly")
        self.filepath_entry.pack(pady=(0, 10))
                
        self.image_preview_label = ttk.Label(self.main_tab)
        self.image_preview_label.pack(pady=(10, 10))

        self.browse_button = ttk.Button(self.main_tab, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=10)

        self.amount_label = ttk.Label(self.main_tab, text="Amount:")
        self.amount_label.pack(pady=(10, 5))
        self.amount_entry = ttk.Entry(self.main_tab)
        self.amount_entry.pack(pady=(0, 10))

        self.upload_button = ttk.Button(self.main_tab, text="Upload Asset", command=self.upload_asset)
        self.upload_button.pack(pady=10)

        self.log_tab = ttk.Frame(self.tab_control, style='TFrame')
        self.tab_control.add(self.log_tab, text='Logs')

        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, height=10, width=50, state='disabled', bg='#26242f', fg='white')
        self.log_text.pack(fill='both', expand=True)
        
        self.log("------------------------------------------------")
        self.log("RO-UPLOADER UI loaded successfully!")
        self.log("Made and coded by 5nz!")
        self.log("Join the discord server: discord.gg/4wffQmV6mR")
        self.log("------------------------------------------------\n")
        
        
        
        self.account_info_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.account_info_tab, text='Account Info')

        self.username_label = ttk.Label(self.account_info_tab, text="Username:")
        self.username_label.pack(pady=(10, 5))
        self.username_value = ttk.Label(self.account_info_tab, text="")
        self.username_value.pack(pady=(0, 10))

        self.user_id_label = ttk.Label(self.account_info_tab, text="User ID:")
        self.user_id_label.pack(pady=(10, 5))
        self.user_id_value = ttk.Label(self.account_info_tab, text="")
        self.user_id_value.pack(pady=(0, 10))

        self.api_key_label = ttk.Label(self.account_info_tab, text="API Key:")
        self.api_key_label.pack(pady=(10, 5))
        self.api_key_value = ttk.Label(self.account_info_tab, text="Click to reveal")
        self.api_key_value.pack(pady=(0, 10))
        self.api_key_value.bind("<Button-1>", self.reveal_api_key)

        self.profile_button = ttk.Button(self.account_info_tab, text="Profile", command=self.open_profile)
        self.profile_button.pack(pady=10)

        self.inventory_button = ttk.Button(self.account_info_tab, text="Inventory", command=self.open_inventory)
        self.inventory_button.pack(pady=10)

        self.load_account_info()


        self.credits_tab = ttk.Frame(self.tab_control, style='TFrame')
        self.tab_control.add(self.credits_tab, text='Credits')
        self.credits_text = ttk.Label(self.credits_tab, text="Made and coded by 5nz", style='TLabel', font=('Helvetica', 12))
        self.credits_text.pack()

        self.github_link = ttk.Label(self.credits_tab, text="https://github.com/5nz", style='Link.TLabel', cursor="hand2", font=('Helvetica', 20, 'underline'), foreground='blue')
        self.github_link.pack()
        self.github_link.bind("<Button-1>", lambda e: self.open_link("https://github.com/5nz"))

        self.discord_link = ttk.Label(self.credits_tab, text="Join the Discord server", style='Link.TLabel', cursor="hand2", font=('Helvetica', 20, 'underline'), foreground='blue')
        self.discord_link.pack()
        self.discord_link.bind("<Button-1>", lambda e: self.open_link("https://discord.gg/4wffQmV6mR"))
        
        self.note_label = ttk.Label(self.credits_tab, text="Note: This tool use's the shitty ROBLOX open cloud API, MEANING this will get flagged down quick and may lead to instant declines!", style='TLabel', font=('Helvetica', 10))
        self.note_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.note_label2 = ttk.Label(self.credits_tab, text="Note: This tool is for educational purposes only. Use at your own risk.", style='TLabel', font=('Helvetica', 10))
        self.note_label2.pack(side=tk.BOTTOM, fill=tk.X)
        self.tab_control.pack(expand=1, fill="both")

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state='disabled')
        self.log_text.yview(tk.END)

    def create_api_key(self):
        cookie = self.cookie_entry.get()
        if cookie:
            self.roblox.config['cookie'] = cookie
            self.roblox.save_config()
            api_key = self.roblox.create_api_key()
            self.log(f"Create API Key Response: {api_key}")
            if "Error" in api_key:
                messagebox.showerror("Error", api_key)
                fs, data = read(resource_path("./Data/SFX/error.wav"))
                sd.play(data, fs)
                sd.wait()
            else:
                messagebox.showinfo("Success", f"API Key Created: {api_key}")
                user_info = self.roblox.get_user_info()
                if user_info is not None:
                    user_info_to_save = {
                        "userID": user_info["id"],
                        "userName": user_info["name"]
                    }
                    self.roblox.save_user_info(user_info_to_save)
                    self.load_account_info()
        else:
            messagebox.showwarning("Error", "Please enter the Roblox cookie.")
            fs, data = read(resource_path("./Data/SFX/error.wav"))
            sd.play(data, fs)
            sd.wait()

    def upload_asset(self):
        asset_file = self.filepath_entry.get()
        amount_str = self.amount_entry.get()
        if asset_file:
            try:
                amount = int(amount_str) if amount_str else 1
                messagebox.showinfo("Uploading", "Starting uploading, please be patient. Check the Logs tab if needed.")
                self.upload_thread = threading.Thread(target=self.perform_uploads, args=(asset_file, amount))
                self.upload_thread.start()
            except ValueError:
                messagebox.showwarning("Error", "Please enter a valid number for the amount.")
        else:
            messagebox.showwarning("Error", "Please enter the asset file path.")

    def perform_uploads(self, asset_file, amount):
        processed_images = []
        
        for _ in range(amount):
            processed_images.append(process_image(asset_file))

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.roblox.start_upload, img_data) for img_data in processed_images]
            results = []
            for i, future in enumerate(as_completed(futures), start=1):
                result = future.result()
                results.append(result)
                self.log(f"Upload Asset Response ({i}/{amount}): {result}")

        success_message = f"Successfully uploaded {amount} assets."
        messagebox.showinfo("Upload Complete", success_message)
        fs, data = read(resource_path("./Data/SFX/upload_Success.wav"))
        sd.play(data, fs)
        sd.wait()
        
    def open_link(self, url):
            import webbrowser
            webbrowser.open(url)

    def browse_file(self):
        filepath = filedialog.askopenfilename()
        self.filepath_entry.config(state="normal")
        self.filepath_entry.delete(0, tk.END)
        self.filepath_entry.insert(0, filepath)
        self.filepath_entry.config(state="readonly")
        self.preview_image(filepath)

    def preview_image(self, filepath):
        image = Image.open(filepath)
        image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(image)
        self.image_preview_label.config(image=photo)
        self.image_preview_label.image = photo
        
    def load_account_info(self):
        user_info = self.roblox.load_user_info()
        if user_info is not None:
            self.username_value.config(text=user_info["userName"])
            self.user_id_value.config(text=str(user_info["userID"]))

    def reveal_api_key(self, event):
        api_key = self.roblox.config.get('api_key')
        if api_key:
            self.api_key_value.config(text=api_key, wraplength=400)
            self.api_key_frame = ttk.Frame(self.account_info_tab)
            self.api_key_frame.pack(pady=(0, 10))

            self.hide_button = ttk.Button(self.api_key_frame, text="Hide", command=self.hide_api_key)
            self.hide_button.pack(side=tk.LEFT, padx=(0, 5))

            self.copy_button = ttk.Button(self.api_key_frame, text="Copy", command=lambda: self.copy_to_clipboard(api_key))
            self.copy_button.pack(side=tk.LEFT, padx=(0, 5))
        else:
            self.api_key_value.config(text="No API key found")
            
    def hide_api_key(self):
        self.api_key_value.config(text="Click to reveal")
        self.api_key_frame.destroy()

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
    def open_profile(self):
        user_info = self.roblox.load_user_info()
        if user_info is not None:
            url = f"https://www.roblox.com/users/{user_info['userID']}/profile"
            self.open_link(url)

    def open_inventory(self):
        user_info = self.roblox.load_user_info()
        if user_info is not None:
            url = f"https://www.roblox.com/users/{user_info['userID']}/inventory#!/accessories"
            self.open_link(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = ROUPLOADERUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass