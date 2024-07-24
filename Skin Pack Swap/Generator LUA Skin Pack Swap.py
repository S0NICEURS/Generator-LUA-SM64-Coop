import tkinter as tk
import ctypes
from tkinter import filedialog, simpledialog, scrolledtext, messagebox
import os

if __name__ == "__main__":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class LuaGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generator LUA: Skin Pack Swap")
        
        self.files = []
        self.model_names = []
        
        # Setup UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for buttons and entry
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        # Entry for pack name
        self.pack_name_label = tk.Label(self.button_frame, text="Pack Name:")
        self.pack_name_label.pack(side=tk.LEFT, padx=5)
        
        self.pack_name_entry = tk.Entry(self.button_frame)
        self.pack_name_entry.pack(side=tk.LEFT, padx=5)
        
        # Entry for pack description
        self.pack_desc_label = tk.Label(self.button_frame, text="Pack Description:")
        self.pack_desc_label.pack(side=tk.LEFT, padx=5)
        
        self.pack_desc_entry = tk.Entry(self.button_frame)
        self.pack_desc_entry.pack(side=tk.LEFT, padx=5)
        
        # Button to add .bin files
        self.add_button = tk.Button(self.button_frame, text="Add .bin file", command=self.add_file)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # Button to generate Lua script
        self.generate_button = tk.Button(self.button_frame, text="Generate Lua Script", command=self.generate_lua_script)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        # Text box to display selected files and generated Lua script
        self.lua_script_text = scrolledtext.ScrolledText(self.root, width=80, height=30)
        self.lua_script_text.pack(pady=10)
        
        # Button to save Lua script to desktop
        self.save_button = tk.Button(self.root, text="Save to Desktop", command=self.save_to_desktop)
        self.save_button.pack(pady=5)
        
    def add_file(self):
        file = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin")])
        if file:
            model_name = simpledialog.askstring("Model Name", f"Enter name for model {os.path.basename(file)}:")
            if model_name:
                self.files.append(file)
                self.model_names.append(model_name)
                self.update_file_list_display()
        
    def generate_lua_script(self):
        if not self.files:
            return
        
        pack_name = self.pack_name_entry.get() or "Custom Skin Pack"
        pack_description = self.pack_desc_entry.get() or "Adds custom skins."

        # Define model variables and lists based on the provided files and names
        model_defs = []
        model_vars = []
        model_list = []

        for file, model_name in zip(self.files, self.model_names):
            file_name = os.path.splitext(os.path.basename(file))[0].lower()
            model_var = f"E_MODEL_{file_name.upper()}"
            model_defs.append(f'{model_var} = smlua_model_util_get_id("{file_name}")')  # Removed _geo suffix
            model_vars.append(model_var)
            model_list.append(f'"{model_name}"')
        
        lua_script = f"""-- name: {pack_name}
-- description: {pack_description}

{'\n'.join(model_defs)}

local wardrobeMode = false

modelSkin = 0

-- Edit these values to add/delete a model --
modelVars = {{nil, {', '.join(model_vars)}}}
modelList = {{'Default', {', '.join(model_list)}}}

modelSkin_limit = 0
for _ in pairs(modelVars) do modelSkin_limit = modelSkin_limit + 1 end

function mario_update_local(m)
    -- Some Stuff --
    if modelSkin <= -1 then
        modelSkin = modelSkin_limit
    end
    if modelSkin >= modelSkin_limit + 1 then
        modelSkin = 0
    end

    if wardrobeMode == true then
        set_mario_animation(m, MARIO_ANIM_STAND_AGAINST_WALL)
    end
    -- Controls --
    if wardrobeMode == true then
        if (m.controller.buttonPressed & R_JPAD) ~= 0 then
            play_sound(SOUND_MENU_CHANGE_SELECT, m.marioObj.header.gfx.cameraToObject)
            modelSkin = modelSkin + 1
        end
        if (m.controller.buttonPressed & L_JPAD) ~= 0 then
            play_sound(SOUND_MENU_CHANGE_SELECT, m.marioObj.header.gfx.cameraToObject)
            modelSkin = modelSkin - 1
        end
    end
    if (m.controller.buttonPressed & D_JPAD) ~= 0 then
        if wardrobeMode == true then
            play_sound(SOUND_MENU_STAR_SOUND_OKEY_DOKEY, m.marioObj.header.gfx.cameraToObject)
            wardrobeMode = false
            return true
        end
        if wardrobeMode == false then
            play_sound(SOUND_MENU_READ_A_SIGN, m.marioObj.header.gfx.cameraToObject)
            wardrobeMode = true
            return true
        end
    end

    -- Models --
    gPlayerSyncTable[0].modelId = modelVars[modelSkin + 1]
end

function mario_update(m)
    if m.playerIndex == 0 then
        mario_update_local(m)
    end

    if gPlayerSyncTable[m.playerIndex].modelId ~= nil then
        obj_set_model_extended(m.marioObj, gPlayerSyncTable[m.playerIndex].modelId)
    end
	
	-- Milne expressions.
	if gPlayerSyncTable[m.playerIndex].modelId == E_MODEL_MILNE then
		-- yawn
		if m.action == ACT_START_SLEEPING and m.actionState == 2 then
			m.marioBodyState.eyeState = 9
		end
		-- snoring
		if m.action == ACT_SLEEPING then
			if m.actionState == 0 then
				if m.marioObj.header.gfx.animInfo.animFrame < 20 then
					m.marioBodyState.eyeState = 9
				elseif m.marioObj.header.gfx.animInfo.animFrame >= 20 then
					m.marioBodyState.eyeState = 10
				end
			elseif m.actionState == 2 then
				if m.marioObj.header.gfx.animInfo.animFrame < 25 then
					m.marioBodyState.eyeState = 9
				elseif m.marioObj.header.gfx.animInfo.animFrame >= 25 then
					m.marioBodyState.eyeState = 10
				end
			else
				m.marioBodyState.eyeState = 10
			end
		end
		-- blushin' after Peach's kiss
		if m.action == ACT_END_PEACH_CUTSCENE then
			if (m.actionTimer >= 136 and m.actionArg == 8) or (m.actionArg == 9 and m.actionTimer <= 60) then
				m.marioBodyState.eyeState = 11
			end
		end
		-- death 'n hurt animations
		if m.action == ACT_STANDING_DEATH or m.action == ACT_ELECTROCUTION or m.action == ACT_WATER_DEATH then
			m.marioBodyState.eyeState = 13
		end
		if m.action == ACT_LAVA_BOOST or
			m.action == ACT_BURNING_FALL or
			m.action == ACT_BURNING_JUMP or
			m.action == ACT_QUICKSAND_DEATH or
			m.action == ACT_GRABBED or
			m.action == ACT_GETTING_BLOWN or
			m.action == ACT_HARD_BACKWARD_AIR_KB or
			m.action == ACT_BACKWARD_AIR_KB or
			m.action == ACT_SOFT_BACKWARD_GROUND_KB or
			m.action == ACT_HARD_FORWARD_AIR_KB or
			m.action == ACT_FORWARD_AIR_KB or
			m.action == ACT_SOFT_FORWARD_GROUND_KB or
			m.action == ACT_THROWN_FORWARD or
			m.action == ACT_THROWN_BACKWARD or
			m.action == ACT_DEATH_EXIT or
			m.action == ACT_BURNING_GROUND then
			m.marioBodyState.eyeState = 12
		end
		if m.action == ACT_HARD_BACKWARD_GROUND_KB or
			m.action == ACT_BACKWARD_GROUND_KB or
			m.action == ACT_HARD_FORWARD_GROUND_KB or
			m.action == ACT_FORWARD_GROUND_KB or
			m.action == ACT_DEATH_EXIT_LAND or
			m.action == ACT_FORWARD_WATER_KB or
			m.action == ACT_BACKWARD_WATER_KB or
			m.action == ACT_GROUND_BONK then
			m.marioBodyState.eyeState = 14
		end
		if m.action == ACT_DEATH_ON_BACK or m.action == ACT_DEATH_ON_STOMACH then
			m.actionTimer = m.actionTimer + 1
			if m.actionTimer >= 30 then
				m.marioBodyState.eyeState = 13
			end
		end
		if m.action == ACT_DROWNING then
			if m.actionState == 0 then
				m.marioBodyState.eyeState = 12
			elseif m.actionState == 1 then
				m.marioBodyState.eyeState = 13
			end
		end
		-- misc
		if m.action == ACT_STAR_DANCE_EXIT or m.action == ACT_STAR_DANCE_NO_EXIT or m.action == ACT_STAR_DANCE_WATER then
			if m.marioBodyState.eyeState < 2 then
				m.marioBodyState.eyeState = 2
			end
		end
		if m.action == ACT_EXIT_LAND_SAVE_DIALOG and m.actionState == 2 then
			if m.marioObj.header.gfx.animInfo.animFrame > 109 and m.marioObj.header.gfx.animInfo.animFrame < 154 then
				m.marioBodyState.eyeState = 15
			elseif m.marioObj.header.gfx.animInfo.animFrame > 0 and m.marioObj.header.gfx.animInfo.animFrame <= 109 then
				m.marioBodyState.eyeState = 12
			end
		end
		if m.action == ACT_FEET_STUCK_IN_GROUND then
			if m.marioObj.header.gfx.animInfo.animFrame < 100 then
				m.marioBodyState.eyeState = 12
			elseif m.marioObj.header.gfx.animInfo.animFrame >= 100 then
				m.marioBodyState.eyeState = 14
			end
		end
		if m.action == ACT_BUTT_STUCK_IN_GROUND then
			if m.marioObj.header.gfx.animInfo.animFrame < 100 then
				m.marioBodyState.eyeState = 12
			elseif m.marioObj.header.gfx.animInfo.animFrame >= 100 then
				m.marioBodyState.eyeState = 14
			end
		end
		if m.action == ACT_PANTING then
			m.marioBodyState.eyeState = 16
		end
		if m.action == ACT_SHIVERING then
			if m.actionState == 0 then
				if m.marioObj.header.gfx.animInfo.animFrame >= 30 then
					m.marioBodyState.eyeState = 16
				else
					m.marioBodyState.eyeState = 17
				end
			else
				m.marioBodyState.eyeState = 17
			end
		end
	end
end

function mario_before_phys_step(m)
    if wardrobeMode == true then
        m.vel.x = 0
        if m.vel.y > 0 then
            m.vel.y = 0
        end
        m.vel.z = 0
    end
end

function hud_char()
    djui_hud_set_resolution(RESOLUTION_DJUI);
    djui_hud_set_font(FONT_MENU);

    local screenHeight = djui_hud_get_screen_height()
    local screenWidth = djui_hud_get_screen_width()
    local scale = 1
    local tscale = 0.8
    local width = 0
    local twidth = 0
    local height = 64 * scale
    local theight = 64 * tscale

    if modelSkin >= modelSkin_limit + 1 then
        width = djui_hud_measure_text(modelList[1]) * scale
    elseif modelSkin <= -1 then
        width = djui_hud_measure_text(modelList[modelSkin_limit + 1]) * scale
    else
        width = djui_hud_measure_text(modelList[modelSkin + 1]) * scale
    end

    if modelSkin >= modelSkin_limit + 1 then
        twidth = djui_hud_measure_text(modelList[1]) * tscale
    elseif modelSkin <= -1 then
        twidth = djui_hud_measure_text(modelList[modelSkin_limit + 1]) * tscale
    else
        twidth = djui_hud_measure_text(modelList[modelSkin + 1]) * tscale
    end

    local y = (screenHeight / 2) - (height / 2) + 300
    local x = (screenWidth / 2) - (width / 2)

    local ty = (screenHeight / 2) - (theight / 2) + 300
    local tx = (screenWidth / 2) - (twidth / 2)

    if wardrobeMode == true then
        if modelSkin >= modelSkin_limit + 1 then
            djui_hud_print_text(modelList[1], x, y, scale)
        elseif modelSkin <= -1 then
            djui_hud_print_text(modelList[modelSkin_limit + 1], x, y, scale)
        else
            djui_hud_print_text(modelList[modelSkin + 1], x, y, scale)
        end

        scale = 0.8
        djui_hud_set_color(255,255,255,123)
        if modelSkin + 1 >= modelSkin_limit + 1 then
            djui_hud_print_text(modelList[1], tx + 500, ty, tscale)
        elseif modelSkin + 1 <= -1 then
            djui_hud_print_text(modelList[modelSkin_limit + 1], tx + 500, ty, tscale)
        else
            djui_hud_print_text(modelList[modelSkin + 2], tx + 500, ty, tscale)
        end

        if modelSkin - 1 >= modelSkin_limit + 1 then
            djui_hud_print_text(modelList[1], tx - 500, ty, tscale)
        elseif modelSkin - 1 <= -1 then
            djui_hud_print_text(modelList[modelSkin_limit + 1], tx - 500, ty, tscale)
        else
            djui_hud_print_text(modelList[modelSkin], tx - 500, ty, tscale)
        end
    end
end

function on_hud_render()
    hud_char()
end

hook_event(HOOK_BEFORE_PHYS_STEP, mario_before_phys_step)
hook_event(HOOK_ON_HUD_RENDER, on_hud_render)
hook_event(HOOK_MARIO_UPDATE, mario_update)

"""

        # Display the generated Lua script in the text box
        self.lua_script_text.delete(1.0, tk.END)
        self.lua_script_text.insert(tk.END, lua_script)

    def save_to_desktop(self):
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  # For Windows
        # desktop = os.path.join(os.path.expanduser("~"), 'Desktop')  # For macOS/Linux
        
        pack_name = self.pack_name_entry.get() or "CustomSkinPack"
        file_name = os.path.join(desktop, f"{pack_name}.lua")
        
        with open(file_name, 'w') as f:
            f.write(self.lua_script_text.get(1.0, tk.END))
        
        messagebox.showinfo("Save Successful", f"Lua script saved to desktop as {file_name}.")

    def update_file_list_display(self):
        self.lua_script_text.delete(1.0, tk.END)
        self.lua_script_text.insert(tk.END, "Selected files:\n")
        for file in self.files:
            self.lua_script_text.insert(tk.END, f"{os.path.basename(file)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LuaGeneratorApp(root)
    root.mainloop()