import sdl2
import ctypes

from src.cpu import *
from src.utils import *

class GFX:
    def __init__(self, emu):

        self.emu = emu
        self.cpu = CPU(self.emu)
        self.utils = Utils(self.emu)

        self.event = threading.Event()  # Create a threading event

        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.screen_mult = 10
        self.screen_width = 64 * self.screen_mult
        self.screen_height = 32 * self.screen_mult

        # Set SDL_GL attributes before creating the window
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 3)

        # Create the window with SDL_WINDOW_OPENGL flag
        self.window = sdl2.SDL_CreateWindow(
            b"c8",  # Window title
            sdl2.SDL_WINDOWPOS_UNDEFINED,  # x position
            sdl2.SDL_WINDOWPOS_UNDEFINED,  # y position
            self.screen_width,  # width
            self.screen_height,  # height
            sdl2.SDL_WINDOW_OPENGL  # flags for OpenGL
        )

        # Create the OpenGL context
        self.gl_context = sdl2.SDL_GL_CreateContext(self.window)
        self.renderer = sdl2.SDL_CreateRenderer(
            self.window,
            -1,
            sdl2.SDL_RENDERER_ACCELERATED
        )

        self.run()


    def handle_events(self):

        event = sdl2.SDL_Event()

        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:

            if event.type == sdl2.SDL_KEYDOWN:

                if event.key.keysym.sym == sdl2.SDLK_F3:

                    self.emu.rom_selection = True

                    rom = self.utils.rom_selection()
                    print(rom)

                    self.emu.setup_system()

                    self.utils.load_file_into_memory(rom)
                    self.utils.load_font_into_memory()

                    self.emu.rom_selection = False

                for i in range (16):
                    if (event.key.keysym.sym == self.emu.key_map[i]):
                        self.emu.key_pressed = self.emu.chip_keys[i]
                        break

            if event.type == sdl2.SDL_KEYUP:

                for i in range (16):
                    if (event.key.keysym.sym != self.emu.key_map[i]):
                        self.emu.key_pressed = -1
                        break

            if event.type == sdl2.SDL_QUIT:
                self.emu.game_running = False


    def run(self):

        while self.emu.game_running:

            self.handle_events()

            if self.emu.delay_timer != 0:
                self.emu.delay_timer = self.emu.delay_timer - 1

            if self.emu.sound_timer != 0:
                self.emu.sound_timer = self.emu.sound_timer - 1

            if not self.emu.waiting_for_keypress or self.emu.rom_selection:

                if not self.emu.decoding or not self.event.is_set():

                    self.emu.decoding = True
                    #self.emu.thread_wait.start()
                    self.cpu.decode_opcode()
                    self.event.set() 
                    # Reset the event for the next iteration
                    self.event.clear()
                    self.emu.decoding = False

            if self.emu.draw_begin:

                height = self.emu.n_nibble
                x_register = self.emu.registers[self.emu.x_nibble]
                y_register = self.emu.registers[self.emu.y_nibble]
                index_end = self.emu.index_register + height

                if x_register <= 40:
                    x_register = x_register % self.emu.screen_width

                if y_register >= 20:
                    y_register = y_register % self.emu.screen_height

                for x, sprite_byte in enumerate(self.emu.memory[self.emu.index_register:index_end]):
                    
                    if height == 0:
                        break

                    for y in range(8):
                        sprite = sprite_byte & (0x80 >> y)
                        pixel_x = (x_register + y) % self.emu.screen_width
                        pixel_y = (y_register + x) % self.emu.screen_height

                        if x_register >= 57:
                            if pixel_x <= height:
                                break

                        if y_register >= 25:
                            if pixel_y <= height:
                                break

                        if sprite != 0:
                            # Check if the pixel is already set to 1
                            if self.emu.display[pixel_y][pixel_x] == 1:
                                self.emu.registers[0xF] = 1

                            # Set the pixel value
                            self.emu.display[pixel_y][pixel_x] ^= 1

                self.emu.draw_begin = False
                self.emu.program_counter += 2

            self.update_display()

            # Here you can add code to update the window content, render graphics, etc.
            # For now, we'll just delay a bit to prevent the loop from running too fast
            # sdl2.SDL_Delay(5)

        # Clean up resources before exiting
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def update_display(self):

        sdl2.SDL_SetRenderDrawColor(self.renderer, self.emu.game_background.r, self.emu.game_background.g, self.emu.game_background.b, self.emu.game_background.a)
        sdl2.SDL_RenderClear(self.renderer)

        rectangles = []
        for y in range(self.emu.screen_height):
            for x in range(self.emu.screen_width):
                if self.emu.display[y][x] == 1:
                    rect = sdl2.SDL_Rect(
                        x * self.emu.screen_multiplier,
                        y * self.emu.screen_multiplier,
                        self.emu.screen_multiplier,
                        self.emu.screen_multiplier
                    )
                    rectangles.append(rect)

        if rectangles:
            sdl2.SDL_SetRenderDrawColor(self.renderer, self.emu.game_foreground.r, self.emu.game_foreground.g, self.emu.game_foreground.b, self.emu.game_foreground.a)
            sdl2.SDL_RenderFillRects(self.renderer, (sdl2.SDL_Rect * len(rectangles))(*rectangles), len(rectangles))

        sdl2.SDL_RenderPresent(self.renderer)