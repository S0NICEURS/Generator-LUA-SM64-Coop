import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Scrollbar, Frame
import os
import json

if __name__ == "__main__":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class LuaGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Generator LUA: Character Select")
        self.master.geometry("900x600")

        self.characters = []

        self.create_widgets()

    def create_widgets(self):
        # Frame for pack name
        pack_name_frame = tk.Frame(self.master)
        pack_name_frame.pack(pady=10, fill=tk.X)

        tk.Label(pack_name_frame, text="Pack Name:").pack(side=tk.LEFT, padx=5)
        self.pack_name_entry = tk.Entry(pack_name_frame, width=50)
        self.pack_name_entry.pack(side=tk.LEFT, padx=5)
        self.pack_name_entry.insert(0, "Custom Character Pack")  # Default name

        # Frame for buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10, fill=tk.X)

        self.add_character_button = tk.Button(button_frame, text="Add Character", command=self.add_character)
        self.add_character_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = tk.Button(button_frame, text="Generate main.lua", command=self.generate_lua_file)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Frame for character list and edit
        self.character_frame = tk.Frame(self.master)
        self.character_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.character_frame)
        self.scrollbar = Scrollbar(self.character_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_data)
        file_menu.add_command(label="Load", command=self.load_data)
        menu_bar.add_cascade(label="Profile", menu=file_menu)
        self.master.config(menu=menu_bar)

    def save_data(self):
        data = {
            "pack_name": self.pack_name_entry.get(),
            "characters": [char.to_dict() for char in self.characters]
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as file:
                json.dump(data, file)
            messagebox.showinfo("Success", "Data saved successfully!")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                data = json.load(file)
            self.pack_name_entry.delete(0, tk.END)
            self.pack_name_entry.insert(0, data.get("pack_name", ""))
            self.characters = []
            for char_data in data.get("characters", []):
                new_char = CharacterConfig.from_dict(self, char_data)
                self.characters.append(new_char)
            self.display_characters()
            messagebox.showinfo("Success", "Data loaded successfully!")






    def add_character(self):
        new_character = CharacterConfig(self)
        if new_character.name:  # Add character only if a valid name is provided
            self.characters.append(new_character)
            self.display_characters()

    def display_characters(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for char in self.characters:
            char_frame = tk.Frame(self.scrollable_frame)
            char_frame.pack(pady=5, fill=tk.X)

            tk.Label(char_frame, text=f"Name: {char.name}").pack(anchor=tk.W, padx=5)
            edit_button = tk.Button(char_frame, text="Edit", command=lambda c=char: self.edit_character(c))
            edit_button.pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(char_frame, text="Delete", command=lambda c=char: self.delete_character(c))
            delete_button.pack(side=tk.LEFT, padx=5)

    def edit_character(self, character):
        CharacterEditWindow(self, character)

    def delete_character(self, character):
        if messagebox.askokcancel("Confirm Delete", f"Are you sure you want to delete character '{character.name}'?"):
            self.characters.remove(character)
            self.display_characters()

    def generate_lua_file(self):
        lua_code = self.generate_lua_code()
        file_path = filedialog.asksaveasfilename(defaultextension=".lua", filetypes=[("Lua files", "*.lua")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(lua_code)
            messagebox.showinfo("Success", "Lua file generated successfully!")

    def generate_lua_code(self):
        pack_name = self.pack_name_entry.get()

        lua_template = f"""-- name: [CS] {pack_name}
-- description: A Template for Character Select to build off of when making your own pack!\\#ff7777\\This Pack requires Character Select to use as a Library!
--[[API Documentation for Character Select can be found below: https://github.com/Squishy6094/character-select-coop/wiki/API-Documentation, Use this if you're curious on how anything here works, code generated by tool Soniceurs]]

"""

        lua_template += "--- MODEL ---\n"
        for char in self.characters:
            model_name = os.path.splitext(os.path.basename(char.model_file))[0]
            lua_template += f"local E_MODEL_{char.name.upper()} = smlua_model_util_get_id(\"{model_name}\")\n"

        lua_template += "\n--- ICON ---\n"
        for char in self.characters:
            icon_name = os.path.splitext(os.path.basename(char.icon_file))[0]
            lua_template += f"local TEX_ICON_{char.name.upper()} = get_texture_info(\"{icon_name}\")\n"

        lua_template += "\n--- VOICE ---\n"
        for char in self.characters:
            lua_template += f"local CUSTOM_VOICETABLE_{char.name.upper()} = {{\n"
            for sound_id, file in char.voice_files.items():
                lua_template += f"    [{sound_id}] = '{os.path.basename(file)}',\n"
            lua_template += "}\n\n"

        lua_template += "--- CHARACTER ---\n"
        lua_template += " \n"
        lua_template += "if _G.charSelectExists then\n"
        for char in self.characters:
            lua_template += f"""
    CT_{char.name.upper()} = _G.charSelect.character_add("{char.name}", {{"{char.description}", " "}}, "{char.creator}", {{r = {char.color[0]:02x}, g = {char.color[1]:02x}, b = {char.color[2]:02x}}}, E_MODEL_{char.name.upper()}, CT_MARIO, TEX_ICON_{char.name.upper()})
    _G.charSelect.character_add_voice(E_MODEL_{char.name.upper()}, CUSTOM_VOICETABLE_{char.name.upper()})
    hook_event(HOOK_CHARACTER_SOUND, function (m, sound)
        if _G.charSelect.character_get_voice(m) == CUSTOM_VOICETABLE_{char.name.upper()} then return _G.charSelect.voice.sound(m, sound) end
    end)
    hook_event(HOOK_MARIO_UPDATE, function (m)
        if _G.charSelect.character_get_voice(m) == CUSTOM_VOICETABLE_{char.name.upper()} then return _G.charSelect.voice.snore(m) end
    end)

"""
        lua_template += "end\n"
        return lua_template

class CharacterConfig:
    CHAR_SOUND_IDS = [
        "CHAR_SOUND_ATTACKED",
        "CHAR_SOUND_DOH",
        "CHAR_SOUND_DROWNING",
        "CHAR_SOUND_DYING",
        "CHAR_SOUND_GROUND_POUND_WAH",
        "CHAR_SOUND_HAHA",
        "CHAR_SOUND_HAHA_2",
        "CHAR_SOUND_HERE_WE_GO",
        "CHAR_SOUND_HOOHOO",
        "CHAR_SOUND_MAMA_MIA",
        "CHAR_SOUND_OKEY_DOKEY",
        "CHAR_SOUND_ON_FIRE",
        "CHAR_SOUND_OOOF",
        "CHAR_SOUND_OOOF2",
        "CHAR_SOUND_PUNCH_HOO",
        "CHAR_SOUND_PUNCH_WAH",
        "CHAR_SOUND_PUNCH_YAH",
        "CHAR_SOUND_SO_LONGA_BOWSER",
        "CHAR_SOUND_TWIRL_BOUNCE",
        "CHAR_SOUND_WAAAOOOW",
        "CHAR_SOUND_WAH2",
        "CHAR_SOUND_WHOA",
        "CHAR_SOUND_YAHOO",
        "CHAR_SOUND_YAHOO_WAHA_YIPPEE",
        "CHAR_SOUND_YAH_WAH_HOO",
        "CHAR_SOUND_YAWNING"
    ]
    @classmethod
    def from_dict(cls, app, data):
        obj = cls.__new__(cls)
        obj.app = app
        obj.name = data["name"]
        obj.model_file = data["model_file"]
        obj.icon_file = data["icon_file"]
        obj.voice_files = data["voice_files"]
        obj.color = data["color"]
        obj.description = data["description"]
        obj.creator = data["creator"]
        return obj

    def to_dict(self):
        return {
            "name": self.name,
            "model_file": self.model_file,
            "icon_file": self.icon_file,
            "voice_files": self.voice_files,
            "color": self.color,
            "description": self.description,
            "creator": self.creator
        }

    def __init__(self, app):
        self.app = app
        self.name = simpledialog.askstring("Character Name", "Enter the character name:")
        self.model_file = None
        self.icon_file = None
        self.voice_files = {}
        self.color = [150, 150, 150]
        self.description = "Default description"
        self.creator = "Default creator"

        if not self.name:
            return

        self.setup_widgets()

    def setup_widgets(self):
        self.window = tk.Toplevel(self.app.master)
        self.window.title("Character Configuration")

        main_frame = tk.Frame(self.window)
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame for character details
        detail_frame = tk.Frame(main_frame)
        detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(detail_frame, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(detail_frame)
        self.name_entry.insert(0, self.name)
        self.name_entry.pack(pady=5)

        tk.Label(detail_frame, text="Description:").pack(pady=5)
        self.description_entry = tk.Entry(detail_frame)
        self.description_entry.insert(0, self.description)
        self.description_entry.pack(pady=5)

        tk.Label(detail_frame, text="Creator:").pack(pady=5)
        self.creator_entry = tk.Entry(detail_frame)
        self.creator_entry.insert(0, self.creator)
        self.creator_entry.pack(pady=5)

        tk.Label(detail_frame, text="Color (RGB):").pack(pady=5)
        self.color_entry = tk.Entry(detail_frame)
        self.color_entry.insert(0, f"{self.color[0]}, {self.color[1]}, {self.color[2]}")
        self.color_entry.pack(pady=5)

        tk.Label(detail_frame, text="Model File:").pack(pady=5)
        self.model_button = tk.Button(detail_frame, text="Choose Model File", command=self.choose_model_file)
        self.model_button.pack(pady=5)

        tk.Label(detail_frame, text="Icon File:").pack(pady=5)
        self.icon_button = tk.Button(detail_frame, text="Choose Icon File", command=self.choose_icon_file)
        self.icon_button.pack(pady=5)

        # Frame for voice files
        voice_frame = tk.Frame(main_frame)
        voice_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.voice_buttons = {}
        for sound_id in self.CHAR_SOUND_IDS:
            frame = tk.Frame(voice_frame)
            frame.pack(fill=tk.X, pady=2)

            label = tk.Label(frame, text=sound_id)
            label.pack(side=tk.LEFT, padx=5)

            button = tk.Button(frame, text="Choose File", command=lambda sid=sound_id: self.choose_voice_file(sid))
            button.pack(side=tk.RIGHT, padx=5)
            self.voice_buttons[sound_id] = button

        # Frame for action buttons
        action_frame = tk.Frame(self.window)
        action_frame.pack(pady=10)

        self.save_button = tk.Button(action_frame, text="Save", command=self.save_character)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(action_frame, text="Cancel", command=self.window.destroy)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def choose_model_file(self):
        self.model_file = filedialog.askopenfilename(filetypes=[("Model files", "*.bin")])
        if self.model_file:
            model_name = os.path.splitext(os.path.basename(self.model_file))[0]
            self.model_button.config(text=model_name)

    def choose_icon_file(self):
        self.icon_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if self.icon_file:
            icon_name = os.path.splitext(os.path.basename(self.icon_file))[0]
            self.icon_button.config(text=f"{icon_name}{os.path.splitext(self.icon_file)[1]}")
            

    def choose_voice_file(self, sound_id):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3;*.ogg")])
        if file_path:
            self.voice_files[sound_id] = file_path
            self.voice_buttons[sound_id].config(text=os.path.basename(file_path))

    def save_character(self):
        self.name = self.name_entry.get().strip()
        self.description = self.description_entry.get().strip()
        self.creator = self.creator_entry.get().strip()
        color_str = self.color_entry.get().strip()
        try:
            self.color = list(map(int, color_str.split(',')))
            if len(self.color) != 3:
                raise ValueError("Invalid color format")
        except ValueError:
            messagebox.showerror("Error", "Invalid color format. Please use RGB values separated by commas.")
            return

        if not self.name or not self.model_file or not self.icon_file:
            messagebox.showerror("Error", "Please fill out all required fields!")
            return

        self.window.destroy()

class CharacterEditWindow:
    def __init__(self, app, character):
        self.app = app
        self.character = character

        self.window = tk.Toplevel(self.app.master)
        self.window.title("Edit Character Configuration")

        self.setup_widgets()

    def setup_widgets(self):
        main_frame = tk.Frame(self.window)
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame for character details
        detail_frame = tk.Frame(main_frame)
        detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(detail_frame, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(detail_frame)
        self.name_entry.insert(0, self.character.name)
        self.name_entry.pack(pady=5)

        tk.Label(detail_frame, text="Description:").pack(pady=5)
        self.description_entry = tk.Entry(detail_frame)
        self.description_entry.insert(0, self.character.description)
        self.description_entry.pack(pady=5)

        tk.Label(detail_frame, text="Creator:").pack(pady=5)
        self.creator_entry = tk.Entry(detail_frame)
        self.creator_entry.insert(0, self.character.creator)
        self.creator_entry.pack(pady=5)

        tk.Label(detail_frame, text="Color (RGB):").pack(pady=5)
        self.color_entry = tk.Entry(detail_frame)
        self.color_entry.insert(0, f"{self.character.color[0]}, {self.character.color[1]}, {self.character.color[2]}")
        self.color_entry.pack(pady=5)

        tk.Label(detail_frame, text="Model File:").pack(pady=5)
        self.model_button = tk.Button(detail_frame, text=os.path.splitext(os.path.basename(self.character.model_file))[0], command=self.choose_model_file)
        self.model_button.pack(pady=5)

        tk.Label(detail_frame, text="Icon File:").pack(pady=5)
        self.icon_button = tk.Button(detail_frame, text=os.path.splitext(os.path.basename(self.character.icon_file))[0], command=self.choose_icon_file)
        self.icon_button.pack(pady=5)

        # Frame for voice files
        voice_frame = tk.Frame(main_frame)
        voice_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.voice_buttons = {}
        for sound_id in CharacterConfig.CHAR_SOUND_IDS:
            frame = tk.Frame(voice_frame)
            frame.pack(fill=tk.X, pady=2)

            label = tk.Label(frame, text=sound_id)
            label.pack(side=tk.LEFT, padx=5)

            button = tk.Button(frame, text=os.path.basename(self.character.voice_files.get(sound_id, "Choose File")), command=lambda sid=sound_id: self.choose_voice_file(sid))
            button.pack(side=tk.RIGHT, padx=5)
            self.voice_buttons[sound_id] = button

        # Frame for action buttons
        action_frame = tk.Frame(self.window)
        action_frame.pack(pady=10)

        self.save_button = tk.Button(action_frame, text="Save", command=self.save_character)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(action_frame, text="Cancel", command=self.window.destroy)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def choose_model_file(self):
        self.character.model_file = filedialog.askopenfilename(filetypes=[("Model files", "*.bin")])
        if self.character.model_file:
            model_name = os.path.splitext(os.path.basename(self.character.model_file))[0]
            self.model_button.config(text=model_name)

    def choose_icon_file(self):
        self.character.icon_file = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if self.character.icon_file:
            icon_name = os.path.splitext(os.path.basename(self.character.icon_file))[0]
            self.icon_button.config(text=f"{icon_name}{os.path.splitext(self.character.icon_file)[1]}")



    def choose_voice_file(self, sound_id):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3;*.ogg")])
        if file_path:
            self.character.voice_files[sound_id] = file_path
            self.voice_buttons[sound_id].config(text=os.path.basename(file_path))

    def save_character(self):
        self.character.name = self.name_entry.get().strip()
        self.character.description = self.description_entry.get().strip()
        self.character.creator = self.creator_entry.get().strip()
        color_str = self.color_entry.get().strip()
        try:
            self.character.color = list(map(int, color_str.split(',')))
            if len(self.character.color) != 3:
                raise ValueError("Invalid color format")
        except ValueError:
            messagebox.showerror("Error", "Invalid color format. Please use RGB values separated by commas.")
            return

        if not self.character.name or not self.character.model_file or not self.character.icon_file:
            messagebox.showerror("Error", "Please fill out all required fields!")
            return

        self.window.destroy()
        self.app.display_characters()

if __name__ == "__main__":
    root = tk.Tk()
    app = LuaGeneratorApp(root)
    root.mainloop()
