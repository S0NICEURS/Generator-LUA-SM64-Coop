import tkinter as tk
import ctypes
from tkinter import filedialog, messagebox, StringVar, DoubleVar
import os
import json

if __name__ == "__main__":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


class LuaGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Generator LUA: Soundtrack Pack")
        self.master.geometry("1890x850")

        self.levels = {
            9: "BobOmb",
            5: "CoolCool",
            6: "CastleWalls",
            24: "ThwompFort",
            10: "Snowman",
            17: "Bowser1",
            19: "Bowser2",
            -2: "PowerUp",
            26: "Courtyard",
            11: "WetDry",
            27: "Slide",
            12: "JollyRoger",
            23: "DireDireDocks",
            20: "SecretWatter",
            4: "BigBoo",
            7: "HazyMaze",
            22: "LethalLava",
            8: "ShiftingSand",
            36: "TallTallMountain",
            13: "TinyHugeIsland",
            14: "TickTockClock",
            15: "RainbowRide",
            21: "Bowser3",
            50: "EXTRA1",
            51: "EXTRA2",
            52: "EXTRA3",
            53: "EXTRA4",
            54: "EXTRA5",
            55: "EXTRA6",
            56: "EXTRA7",
            57: "EXTRA8",
            58: "EXTRA9",
            59: "EXTRA10",
            60: "EXTRA11",
            
        }

        self.audio_files = {}
        self.names = {}

        self.create_widgets()
        self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Profile", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_profile)
        file_menu.add_command(label="Load", command=self.load_profile)

    def save_profile(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        data = {
            "script_name": self.script_name_var.get(),
            "script_description": self.script_description_var.get(),
            "star_select_file": self.star_select_var.get(),
            "lose_file": self.lose_var.get(),
            "levels": {}
        }

        for level_id in self.levels.keys():
            data["levels"][level_id] = {
                "audio_name": self.audio_vars[level_id].get(),
                "loop_end": self.loop_end_vars[level_id].get(),
                "volume": self.volume_vars[level_id].get(),
                "name": self.name_vars[level_id].get()
            }

        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Success", f"Profile saved successfully:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def load_profile(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                self.parse_profile_data(data)
            messagebox.showinfo("Success", f"Profile loaded successfully:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def parse_profile_data(self, data):
        self.script_name_var.set(data.get("script_name", "Soundtrack Pack"))
        self.script_description_var.set(data.get("script_description", "Replaces basic SM64 OST"))
        self.star_select_var.set(data.get("star_select_file", "star_select_sims.ogg"))
        self.lose_var.set(data.get("lose_file", "lose.ogg"))

        levels = data.get("levels", {})
        for level_id, details in levels.items():
            if int(level_id) in self.audio_vars:
                self.audio_vars[int(level_id)].set(details.get("audio_name", ""))
                self.loop_end_vars[int(level_id)].set(details.get("loop_end", 60.0))
                self.volume_vars[int(level_id)].set(details.get("volume", 0.5))
                self.name_vars[int(level_id)].set(details.get("name", ""))

    def create_widgets(self):
        # Create a canvas and a vertical scrollbar
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)

        # Create a frame for the canvas
        self.canvas_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

        # Pack the canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.level_frame = tk.Frame(self.canvas_frame)
        self.level_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.level_frame, text="Select Audio File and Set Volume for Each Level").pack(pady=10)

        self.audio_vars = {}
        self.name_vars = {}
        self.volume_vars = {}
        self.loop_end_vars = {}

        for level_id, level_name in self.levels.items():
            frame = tk.Frame(self.level_frame)
            frame.pack(pady=5, fill=tk.X)

            # Level name and browse button on the same line
            level_label = tk.Label(frame, text=level_name, width=20, anchor="w", font=("Arial", 8))
            level_label.pack(side=tk.LEFT, padx=5, fill=tk.X)

            audio_var = StringVar()
            audio_entry = tk.Entry(frame, textvariable=audio_var, width=30, font=("Arial", 8))
            audio_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.audio_vars[level_id] = audio_var

            browse_button = tk.Button(frame, text="Browse", command=lambda lid=level_id: self.browse_audio_file(lid), font=("Arial", 8))
            browse_button.pack(side=tk.LEFT, padx=5)

            # Text field for name
            name_label = tk.Label(frame, text="Name:", font=("Arial", 8))
            name_label.pack(side=tk.LEFT, padx=5)
            name_var = StringVar(value="")
            name_entry = tk.Entry(frame, textvariable=name_var, width=40, font=("Arial", 8))
            name_entry.pack(side=tk.LEFT, padx=5)
            self.name_vars[level_id] = name_var

            # Volume control
            volume_label = tk.Label(frame, text="Volume:", font=("Arial", 8))
            volume_label.pack(side=tk.LEFT, padx=5)
            volume_var = DoubleVar(value=0.5)
            volume_scale = tk.Scale(frame, variable=volume_var, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, length=200, sliderlength=20, font=("Arial", 8))
            volume_scale.pack(side=tk.LEFT, padx=5)
            self.volume_vars[level_id] = volume_var

            # Loop end control
            loop_end_label = tk.Label(frame, text="LoopEnd:", font=("Arial", 8))
            loop_end_label.pack(side=tk.LEFT, padx=5)
            loop_end_var = DoubleVar(value=60.0)
            loop_end_entry = tk.Entry(frame, textvariable=loop_end_var, width=10, font=("Arial", 8))
            loop_end_entry.pack(side=tk.LEFT, padx=5)
            self.loop_end_vars[level_id] = loop_end_var

        # Update scroll region
        self.canvas_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Frame for the script name and description
        meta_frame = tk.Frame(self.master)
        meta_frame.pack(pady=10)

        tk.Label(meta_frame, text="Name of Mod:", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        self.script_name_var = StringVar(value="Soundtrack Pack")
        tk.Entry(meta_frame, textvariable=self.script_name_var, width=50, font=("Arial", 8)).pack(side=tk.LEFT, padx=5)

        tk.Label(meta_frame, text="Description:", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        self.script_description_var = StringVar(value="Replaces basic SM64 OST")
        tk.Entry(meta_frame, textvariable=self.script_description_var, width=50, font=("Arial", 8)).pack(side=tk.LEFT, padx=5)

        # Frame for .ogg files in main2
        ogg_frame = tk.Frame(self.master)
        ogg_frame.pack(pady=10)

        tk.Label(ogg_frame, text="SAMPLE_STAR_SELECT:", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        self.star_select_var = StringVar(value="star_select_sims.ogg")
        tk.Entry(ogg_frame, textvariable=self.star_select_var, width=30, font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(ogg_frame, text="Browse", command=lambda: self.browse_ogg_file(self.star_select_var), font=("Arial", 8)).pack(side=tk.LEFT, padx=5)

        tk.Label(ogg_frame, text="SAMPLE_LOSE:", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        self.lose_var = StringVar(value="lose.ogg")
        tk.Entry(ogg_frame, textvariable=self.lose_var, width=30, font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(ogg_frame, text="Browse", command=lambda: self.browse_ogg_file(self.lose_var), font=("Arial", 8)).pack(side=tk.LEFT, padx=5)

        # Frame for generating Lua file
        gen_frame = tk.Frame(self.master)
        gen_frame.pack(pady=10)

        self.generate_button = tk.Button(gen_frame, text="Generate Lua Script", command=self.generate_lua_file)
        self.generate_button.pack()

    def browse_audio_file(self, level_id):
        file = filedialog.askopenfilename(
            filetypes=[("Audio files", "*.ogg")],
            title=f"Select Audio File for Level {level_id}"
        )
        if file:
            file_name = os.path.basename(file)
            self.audio_vars[level_id].set(file_name)

    def browse_ogg_file(self, var):
        file = filedialog.askopenfilename(
            filetypes=[("Audio files", "*.ogg")],
            title="Select .ogg File"
        )
        if file:
            file_name = os.path.basename(file)
            var.set(file_name)

    def generate_lua_file(self):
        lua_file_path = filedialog.asksaveasfilename(defaultextension=".lua", filetypes=[("Lua files", "*.lua")])

        if not lua_file_path:
            return

        try:
            with open(lua_file_path, "w") as file:
                file.write(self.generate_lua_code())
            messagebox.showinfo("Success", f"Lua file generated successfully:\n{lua_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def load_file(self):
        lua_file_path = filedialog.askopenfilename(filetypes=[("Lua files", "*.lua")])
        if not lua_file_path:
            return
        try:
            with open(lua_file_path, "r") as file:
                content = file.read()
                self.parse_lua_code(content)
            messagebox.showinfo("Success", f"Lua file loaded successfully:\n{lua_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_file(self):
        self.generate_lua_file()

    def parse_lua_code(self, content):
        self.reset_fields()  # Reset all fields before parsing
        lines = content.splitlines()
        for line in lines:
            if line.startswith("["):
                parts = line.split(" = {")
                level_id = int(parts[0][1:-1])
                details = parts[1].strip("},")
                details_parts = details.split(", ")
                audio_name = details_parts[0].split("'")[1]
                loop_end = float(details_parts[1].split(" = ")[1])
                volume = float(details_parts[3].split(" = ")[1])
                name = details_parts[4].split("\"")[1]
                if level_id in self.audio_vars:
                    self.audio_vars[level_id].set(audio_name)
                    self.loop_end_vars[level_id].set(loop_end)
                    self.volume_vars[level_id].set(volume)
                    self.name_vars[level_id].set(name)

    def reset_fields(self):
        for var in self.audio_vars.values():
            var.set("")
        for var in self.name_vars.values():
            var.set("")
        for var in self.volume_vars.values():
            var.set(0.5)
        for var in self.loop_end_vars.values():
            var.set(60.0)

    def generate_lua_code(self):
        script_name = self.script_name_var.get()
        script_description = self.script_description_var.get()
        
        star_select_file = self.star_select_var.get()
        lose_file = self.lose_var.get()
        
        lua_template = f"""

-- name: {script_name}
-- description: {script_description}

function main1()
-- The code merger and this LUA code is generated from the tool created by Soniceurs (Generator LUA Soundtrack Pack)

-----------------------------------------------------------------------------
--                                Music Mod                                --
-----------------------------------------------------------------------------
local bgms = {{
"""

        for level_id, audio_var in self.audio_vars.items():
            audio_name = audio_var.get()
            name = self.name_vars.get(level_id, StringVar(value="")).get()
            volume = self.volume_vars.get(level_id, DoubleVar(value=0.5)).get()
            loop_end = self.loop_end_vars.get(level_id, DoubleVar(value=60.0)).get()
            if audio_name:
                lua_template += f"\t[{level_id}] = {{audio='{audio_name}', loopEnd = {loop_end}, loopStart = 0, volume = {volume}, name=\"{name}\"}},\n"

        lua_template += f"""
}}



--Feel free to turn this off if (you don't want to show the music name in the pause menu
local pauseMenuShouldShowMusic = false
local pauseMenuMusicRGBA = {{200,200,200,255}}

--Don't know what course ID to put for a map? No worries. Just turn this to true, and the pause menu will show the course number in the corner.
--This requires pauseMenuShouldShowMusic to be true to show up.
local pauseMenuShowLevelID = false

--Below here is just a bunch of internal stuff.
--Feel free to copy/paste/alter it as you like in your own works. I'd like to ask for credit in the form of a lua comment, but I'm not a stickler about it.
--Apologies if any of the code is ugly. I have little lua experience compared to some other languages.
local curMap = -1
local audioMainPaused = false
local audioMain = nil --Used for the main audio
local audioSpecial = nil --Used for things like cap music
local audioCurSeq = nil
function handleMusic()
	------------------------------------------------------
    --          Handle stopping/starting of music       --
	------------------------------------------------------
	--Handle main course music
    if (curMap ~= gNetworkPlayers[0].currLevelNum and gMarioStates[0].area.macroObjects ~= nil) then
        curMap = gNetworkPlayers[0].currLevelNum
		audioCurSeq = get_current_background_music()
        if (audioMain ~= nil) then
            audio_stream_stop(audioMain)
            audio_stream_destroy(audioMain)
            audioMain = nil
        end
        if (bgms[curMap] ~= nil and bgms[curMap].audio ~= nil) then 
            set_background_music(0,0,0)
            audioMain = audio_stream_load(bgms[curMap].audio)
            if (audioMain ~= nil) then
                audio_stream_set_looping(audioMain, true)
                audio_stream_play(audioMain, true, bgms[curMap].volume);
                print("Playing new audio " .. bgms[curMap].name)
            else
                djui_popup_create('Missing audio!: ' .. bgms[curMap].audio, 10)
                print("Attempted to load filed audio file, but couldn't find it on the system: " .. bgms[curMap].audio)
            end
        else
            print("No audio for this map, so not stopping default: " .. curMap)
        end
    end
	--Handle cap music
	if (gMarioStates[0].capTimer > 0 and bgms[-2] ~= nil) then
		--Handle pausing main streamed music, if applicable.
		if (audioMain ~= nil and audioMainPaused == false) then
			audioMainPaused = true
			audio_stream_pause(audioMain)
		end
		--Start up cap music if it's defined.
		if (audioSpecial == nil) then
            set_background_music(0,0,0)
			stop_cap_music()
			audioSpecial = audio_stream_load(bgms[-2].audio)
			if (audioSpecial ~= nil) then
				audio_stream_set_looping(audioSpecial, true)
				audio_stream_play(audioSpecial, true, bgms[-2].volume)
				print("Playing cap audio " .. bgms[-2].name)
			else
				djui_popup_create('Missing audio!: ' .. bgms[-2].audio, 3)
                print("Attempted to load filed audio file, but couldn't find it on the system: " .. bgms[-2].audio)
			end
		end	
	else
		if (audioSpecial ~= nil) then
			audio_stream_stop(audioSpecial)
			audio_stream_destroy(audioSpecial)
			audioSpecial = nil
			if (audioMain ~= nil and audioMainPaused == true) then
				audioMainPaused = false
				audio_stream_play(audioMain, false, bgms[curMap].volume)
			else
				set_background_music(0, audioCurSeq, 10) 
			
			end
		end
	end
	------------------------------------------------------
    --                Handle music looping              --
	------------------------------------------------------
    if (audioMain ~= nil) then 
		local curPosition = audio_stream_get_position(audioMain)
		if (curPosition >= bgms[curMap].loopEnd ) then
			local minus = bgms[curMap].loopStart - bgms[curMap].loopEnd
			audio_stream_set_position(audioMain, curPosition - math.abs(minus))
		end
    end
	if (audioSpecial ~= nil) then
		local curPosition = audio_stream_get_position(audioSpecial)
		if (curPosition >= bgms[-2].loopEnd) then
			local minus = bgms[-2].loopStart - bgms[-2].loopEnd
			audio_stream_set_position(audioSpecial, curPosition - math.abs(minus))
		end
	end
end

function hud_render()
    if (pauseMenuShouldShowMusic == true and is_game_paused()) then
        djui_hud_set_resolution(RESOLUTION_DJUI);
        djui_hud_set_font(FONT_NORMAL);
        local screenWidth = djui_hud_get_screen_width()
		local screenHeight = djui_hud_get_screen_height()
        local height = 64
        local y = screenHeight - height
        djui_hud_set_color(pauseMenuMusicRGBA[1], pauseMenuMusicRGBA[2], pauseMenuMusicRGBA[3], pauseMenuMusicRGBA[4]);		
		local text = "";
		if (pauseMenuShowLevelID == true) then
			text = "Level ID: " .. gNetworkPlayers[0].currLevelNum
		elseif (audioSpecial ~= nil) then
			text = "Music: " .. bgms[-2].name
		elseif (audioMain ~= nil) then
			text = "Music: " .. bgms[curMap].name
		end
		djui_hud_print_text(text, 5, y, 1);
    end
end



--- @param m MarioState
function on_sit_action(m)
	if m.playerIndex == 0 then
		if (m.action == ACT_DISAPPEARED or m.action == ACT_STAR_DANCE_EXIT or m.action == ACT_STAR_DANCE_NO_EXIT or m.action == ACT_STAR_DANCE_WATER or m.action == ACT_SLEEPING) and (audioMain ~= nil and audioMainPaused == false) then
			audioMainPaused = true
			audio_stream_pause(audioMain)
		else
			if audioMain ~= nil and audioMainPaused == true then
				audioMainPaused = false
				audio_stream_play(audioMain, false, bgms[curMap].volume)
			end
		end
	end
end

hook_event(HOOK_ON_SET_MARIO_ACTION, on_sit_action)

function hud_render()
	if pauseMenuShouldShowMusic == true and is_game_paused() then
		djui_hud_set_resolution(RESOLUTION_DJUI)
		djui_hud_set_font(FONT_NORMAL)
		local screenWidth = djui_hud_get_screen_width()
		local screenHeight = djui_hud_get_screen_height()
		local height = 64
		local y = screenHeight - height
		djui_hud_set_color(pauseMenuMusicRGBA[1], pauseMenuMusicRGBA[2], pauseMenuMusicRGBA[3], pauseMenuMusicRGBA[4])
		local text = ""
		if pauseMenuShowLevelID == true then
			text = "Level ID: " .. gNetworkPlayers[0].currLevelNum
		elseif audioSpecial ~= nil then
			text = "Music: " .. bgms[-2].name
		elseif audioMain ~= nil then
			text = "Music: " .. bgms[curMap].name
		end
		djui_hud_print_text(text, 5, y, 1)
	end
end

hook_event(HOOK_ON_HUD_RENDER, hud_render)
-- Remove or comment out the following lines as they are for replacing audio sequences that you don't have:
-- smlua_audio_utils_replace_sequence(SEQ_EVENT_CUTSCENE_COLLECT_STAR, 34, 0, "silent_star")
-- smlua_audio_utils_replace_sequence(SEQ_EVENT_CUTSCENE_COLLECT_KEY, 34, 0, "silent_star")
hook_event(HOOK_UPDATE, handleMusic)


hook_event(HOOK_ON_HUD_RENDER, hud_render)
hook_event(HOOK_UPDATE, handleMusic)
-----------------------------------------------------------------------------
--                           Music Mod End                                 --
-----------------------------------------------------------------------------

end

-- Code de main2.lua encapsulé dans main2()
function main2()
--This file fixes some of the problems with music mods, including the bug that makes bosses and other music play at the same time as the samples, 
--and it also adds some custom sfx. (by 6b)
local SAMPLE_STAR_SELECT = audio_sample_load('{star_select_file}')
local SAMPLE_LOSE = audio_sample_load('{lose_file}')


function nomusic()
	for i = 0, 38, 1 do
		stop_background_music(SEQ_LEVEL_INSIDE_CASTLE)
		stop_background_music(SEQ_LEVEL_GRASS)
		stop_background_music(SEQ_EVENT_BOSS)
		stop_background_music(SEQ_EVENT_POWERUP)
		stop_background_music(SEQ_EVENT_METAL_CAP)
		stop_background_music(SEQ_EVENT_RACE)
		stop_background_music(SEQ_LEVEL_SLIDE)
		stop_background_music(SEQ_LEVEL_SNOW)
		stop_background_music(SEQ_LEVEL_KOOPA_ROAD)
		stop_background_music(SEQ_LEVEL_BOSS_KOOPA_FINAL)
		stop_background_music(SEQ_LEVEL_HOT)
		stop_background_music(SEQ_MENU_TITLE_SCREEN)
		stop_background_music(SEQ_LEVEL_SPOOKY)
		stop_background_music(SEQ_LEVEL_WATER)
		stop_background_music(SEQ_LEVEL_BOSS_KOOPA)
		stop_background_music(SEQ_LEVEL_UNDERGROUND)
		stop_background_music(0x53)
		stop_background_music(0x41)
		stop_background_music(0x65)
		stop_background_music(0x66)
		stop_shell_music()
		stop_background_music(0x16)
		stop_background_music(0x24)
		stop_background_music(SEQ_LEVEL_BOSS_KOOPA_FINAL)
		stop_background_music(SEQ_EVENT_CUTSCENE_ENDING)
		stop_background_music(SEQ_EVENT_CUTSCENE_CREDITS)
		stop_background_music(SEQ_EVENT_PEACH_MESSAGE)
		stop_background_music(SEQ_EVENT_CUTSCENE_LAKITU)
		stop_background_music(SEQ_EVENT_CUTSCENE_INTRO)
		stop_background_music(SEQ_EVENT_CUTSCENE_VICTORY)
		stop_background_music(SEQ_MENU_FILE_SELECT)
    end
end


--- @param m MarioState
function on_mama_action(m)
	if m.playerIndex == 0 then
		if m.action == ACT_STAR_DANCE_EXIT or m.action == ACT_STAR_DANCE_NO_EXIT or m.action == ACT_STAR_DANCE_WATER then
			--audio_stream_play(STREAM_STAR, false, 1)
			--audio_stream_set_looping(STREAM_STAR, false)
		end
	end
end

hook_event(HOOK_ON_SET_MARIO_ACTION, on_mama_action)

--- @param m MarioState
function on_sleep_action(m)
	if m.playerIndex == 0 then
		-- Define behavior for sleep action if needed
	end
end

hook_event(HOOK_ON_SET_MARIO_ACTION, on_sleep_action)

hook_event(HOOK_UPDATE, nomusic)


function musicremplace()
	if get_current_background_music() == SEQ_MENU_STAR_SELECT then
		stop_background_music(SEQ_MENU_STAR_SELECT)
		audio_sample_play(SAMPLE_STAR_SELECT, gMarioStates[0].marioObj.header.gfx.cameraToObject, 2)
    end
end


	local deathTable = {{
		[ACT_DEATH_ON_STOMACH] = true,
		[ACT_DEATH_ON_BACK] = true,
		[ACT_EATEN_BY_BUBBA] = true,
		[ACT_SUFFOCATION] = true,
		[ACT_STANDING_DEATH] = true,
		[ACT_QUICKSAND_DEATH] = true,
		[ACT_DROWNING] = true,
	}}

	
	function on_set_mario_action(m)
		if deathTable[m.action] then
				audio_sample_play(SAMPLE_LOSE, {{x = 0, y = 0, z = 0}}, 2)
		end
	end



hook_event(HOOK_UPDATE, musicremplace)
hook_event(HOOK_ON_SET_MARIO_ACTION, on_set_mario_action)



end

main1()
main2()

"""

        return lua_template

if __name__ == "__main__":
    root = tk.Tk()
    app = LuaGeneratorApp(root)
    root.mainloop()