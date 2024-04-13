import sdl2

from src.utils import *
from src.gfx import *

class Emulator():

    def __init__(self):

        print("Emulator Starting...")

        self.setup_system()

        self.utils = Utils(self)

        self.initialize_system()

    def initialize_system(self):

        print("Initializing System...")

        # Create an Event object
        self.event = threading.Event()

        # Start the threads
        self.thread_wait = threading.Thread(target=self.utils.wait_for_event)
        self.thread_set = threading.Thread(target=self.utils.set_event)

        for i in range(16):
            self.registers[i] = 0

        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/1-chip8-logo.ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/2-ibm-logo.ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/3-corax+.ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/4-flags.ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/5-quirks.ch8")
        self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/6-keypad.ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/7-beep.ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/tests/8-scrolling.ch8")

        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/works_somewhat/Tank Warfare (unknown author)(197x).ch8")
        #self.utils.load_file_into_memory("/home/mitigd/Projects/c++/class_share_again/build/linux/games/works_somewhat/8ce 8ttorney Disk1 (by SysL)(2016).ch8")

        self.utils.load_font_into_memory()

        self.game_running = True

        GFX(self)
        
    def setup_system(self):

        # CPU
        self.delay_timer = 0
        self.sound_timer = 0
        self.program_counter = 0x200
        self.index_register = 0x0000
        self.nibble = 0
        self.x_nibble = 0
        self.y_nibble = 0
        self.n_nibble = 0
        self.nn_nibble = 0
        self.nnn_nibble = 0
        self.memory = bytearray(4096)
        self.stack = []
        self.registers = {}
        self.stack = []
        self.opcode = 0

        # GFX
        self.screen_width = 64
        self.screen_height = 32
        self.screen_multiplier = 10
        self.font_width = 12
        self.font_height = 10
        self.game_background = sdl2.SDL_Color(255, 191, 0, 255)
        self.game_foreground = sdl2.SDL_Color(100, 60, 0, 255)
        self.display = [[0 for _ in range(64)] for _ in range(32)]

        # INPUT
        self.key_map = [
            sdl2.SDLK_1, sdl2.SDLK_2, sdl2.SDLK_3, sdl2.SDLK_4,
            sdl2.SDLK_q, sdl2.SDLK_w, sdl2.SDLK_e, sdl2.SDLK_r,
            sdl2.SDLK_a, sdl2.SDLK_s, sdl2.SDLK_d, sdl2.SDLK_f,
            sdl2.SDLK_z, sdl2.SDLK_x, sdl2.SDLK_c, sdl2.SDLK_v
        ]
        self.chip_keys = [
            0x1, 0x2, 0x3, 0xC,
            0x4, 0x5, 0x6, 0xD,
            0x7, 0x8, 0x9, 0xE,
            0xA, 0x0, 0xB, 0xF
        ]
        self.key_pressed = -1

        # UTILS
        self.file_start = 0x200
        self.font_start = 0x50

        # GAMESTATE
        self.game_running = True
        self.decoding = False
        self.waiting_for_keypress = False
        self.draw_begin = False
        self.clear_screen = False
        self.rom_selection = False

        for i in range(16):
            self.registers[i] = 0