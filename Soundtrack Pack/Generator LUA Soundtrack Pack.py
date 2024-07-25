import tkinter as tk
import ctypes
from tkinter import filedialog, messagebox, StringVar, DoubleVar
import os

if __name__ == "__main__":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class LuaGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Generator LUA: Soundtrack Pack")
        self.master.geometry("1777x800")  # Increased width for better visibility

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
            # Extract just the file name from the path
            file_name = os.path.basename(file)
            self.audio_vars[level_id].set(file_name)

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

    def get_loop_end(self, audio_name):
        """Return an estimated loop end value based on the file extension."""
        if audio_name.endswith(".ogg"):
            return 60.0  # Approximate value for OGG files
        elif audio_name.endswith(".mp3"):
            return 60.0  # Approximate value for MP3 files
        else:
            return 60.0  # Default value if unknown format

    def generate_lua_code(self):
        script_name = self.script_name_var.get()
        script_description = self.script_description_var.get()
        
        lua_template = f"""

-- name: {script_name}
-- description: {script_description}

function main1()

-- description: {script_description}
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
            if audio_name:
                loop_end = self.get_loop_end(audio_name)
                lua_template += f"\t[{level_id}] = {{audio='{audio_name}', loopEnd = {loop_end}, loopStart = 0, volume = {volume}, name=\"{name}\"}},\n"

        lua_template += """
}



--Feel free to turn this off if you don't want to show the music name in the pause menu
local pauseMenuShouldShowMusic = true
local pauseMenuMusicRGBA = {200, 200, 200, 255}

--Don't know what course ID to put for a map? No worries. Just turn this to true, and the pause menu will show the course number in the corner.
--This requires pauseMenuShouldShowMusic to be true to show up.
local pauseMenuShowLevelID = false

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
	if curMap ~= gNetworkPlayers[0].currLevelNum and gMarioStates[0].area.macroObjects ~= nil then
		curMap = gNetworkPlayers[0].currLevelNum
		audioCurSeq = get_current_background_music()
		if audioMain ~= nil then
			audio_stream_stop(audioMain)
			audio_stream_destroy(audioMain)
			audioMain = nil
		end
		if bgms[curMap] ~= nil and bgms[curMap].audio ~= nil then
			set_background_music(0, 0, 0)
			audioMain = audio_stream_load(bgms[curMap].audio)
			if audioMain ~= nil then
				audio_stream_set_looping(audioMain, true)
				audio_stream_play(audioMain, true, bgms[curMap].volume)
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
	if gMarioStates[0].capTimer > 0 and bgms[-2] ~= nil then
		--Handle pausing main streamed music, if applicable.
		if audioMain ~= nil and audioMainPaused == false then
			audioMainPaused = true
			audio_stream_pause(audioMain)
		end
		--Start up cap music if it's defined.
		if audioSpecial == nil then
			set_background_music(0, 0, 0)
			stop_cap_music()
			audioSpecial = audio_stream_load(bgms[-2].audio)
			if audioSpecial ~= nil then
				audio_stream_set_looping(audioSpecial, true)
				audio_stream_play(audioSpecial, true, bgms[-2].volume)
				print("Playing cap audio " .. bgms[-2].name)
			else
				djui_popup_create('Missing audio!: ' .. bgms[-2].audio, 3)
				print("Attempted to load filed audio file, but couldn't find it on the system: " .. bgms[-2].audio)
			end
		end
	else
		if audioSpecial ~= nil then
			audio_stream_stop(audioSpecial)
			audio_stream_destroy(audioSpecial)
			audioSpecial = nil
			if audioMain ~= nil and audioMainPaused == true then
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
	if audioMain ~= nil then
		local curPosition = audio_stream_get_position(audioMain)
		if curPosition >= bgms[curMap].loopEnd then
			local minus = bgms[curMap].loopStart - bgms[curMap].loopEnd
			audio_stream_set_position(audioMain, curPosition - math.abs(minus))
		end
	end
	if audioSpecial ~= nil then
		local curPosition = audio_stream_get_position(audioSpecial)
		if curPosition >= bgms[-2].loopEnd then
			local minus = bgms[-2].loopStart - bgms[-2].loopEnd
			audio_stream_set_position(audioSpecial, curPosition - math.abs(minus))
		end
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

end

-- Code de main2.lua encapsulé dans main2()
function main2()
--This file fixes some of the problems with music mods, including the bug that makes bosses and other music play at the same time as the samples, 
--and it also adds some custom sfx. (by 6b)

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
			audio_stream_play(STREAM_STAR, false, 1)
			audio_stream_set_looping(STREAM_STAR, false)
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
-- Remove hook_event(HOOK_UPDATE, musicremplace) as the function is not defined

end

main1()
main2()



"""

        return lua_template

if __name__ == "__main__":
    root = tk.Tk()
    app = LuaGeneratorApp(root)
    root.mainloop()