import threading, subprocess, os

class Utils:

    def __init__(self, emu):

        self.emu = emu

    def load_file_into_memory(self, file):

        rom_data = ""
        try:
            with open(file, 'rb') as f:
                rom_data = f.read()
        except FileNotFoundError:
            print("File not found or unable to open file")
        except Exception as e:
            print("An error occurred:", e)

        for byte_value in rom_data:
            self.emu.memory[self.emu.file_start] = byte_value
            self.emu.file_start += 1

    def load_font_into_memory(self):

        font_data = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for byte_value in font_data:
            self.emu.memory[self.emu.font_start] = byte_value
            self.emu.font_start += 1

    
    def rom_selection(self):

        # Get the current working directory
        current_directory = os.getcwd()

        # Run zenity to select a file
        result = subprocess.run(['zenity', '--file-selection', '--filename', current_directory], capture_output=True, text=True)

        # Check if zenity was successful and a file was selected
        if result.returncode == 0 and result.stdout.strip():
            selected_file = result.stdout.strip()
            print("Selected file:", selected_file)
            return selected_file
        else:
            print("No file selected.")
            return None

    def wait_for_event(self):
        print("Waiting for event to be set...")
        self.emu.event.wait() 
        print("Event is set!")

    def set_event(self):
        print("Setting event...")
        self.emu.event.set()