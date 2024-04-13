import re, math, random

from src.utils import *

class CPU():

    def __init__(self, emu):

        self.emu = emu
        self.utils = Utils(self.emu)

        self.opcode_regex_map = {
            re.compile(r'^0[0-9]E0$'): self.opcode_clear_screen,
            re.compile(r'^0[0-9]EE$'): self.opcode_ret,
            re.compile(r'^1'): self.opcode_jump,
            re.compile(r'^2'): self.opcode_call,
            re.compile(r'^3'): self.opcode_skip_vx_equals_nn,
            re.compile(r'^4'): self.opcode_skip_vx_not_equals_nn,
            re.compile(r'^5'): self.opcode_skip_vx_equals_vy,
            re.compile(r'^6'): self.opcode_set_vx_equals_nn,
            re.compile(r'^7'): self.opcode_set_vx_plus_nn,
            re.compile(r'^8[0-9A-F][0-9A-F]0$'): self.opcode_set_vx_equals_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]1$'): self.opcode_set_vx_or_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]2$'): self.opcode_set_vx_and_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]3$'): self.opcode_set_vx_xor_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]4$'): self.opcode_set_vx_add_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]5$'): self.opcode_set_vx_sub_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]6$'): self.opcode_set_vx_shr_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]7$'): self.opcode_set_vx_subn_vy,
            re.compile(r'^8[0-9A-F][0-9A-F]E$'): self.opcode_set_vx_shl_vy,
            re.compile(r'^9'): self.opcode_set_vx_not_equals_vy,
            re.compile(r'^A'): self.opcode_set_i_equals_nnn,
            re.compile(r'^B'): self.opcode_jump_nnn_plus_vzero,
            re.compile(r'^C'): self.opcode_randombyte_and_nn,
            re.compile(r'^D'): self.opcode_draw,
            re.compile(r'^E[0-9A-F]9E$'): self.opcode_skip_if_key_in_vx,
            re.compile(r'^E[0-9A-F]A1$'): self.opcode_skip_if_key_not_in_vx,
            re.compile(r'^F[0-9A-F]07$'): self.opcode_set_vx_equals_delay_timer,
            re.compile(r'^F[0-9A-F]0A$'): self.opcode_wait_keypress_store_vx,
            re.compile(r'^F[0-9A-F]15$'): self.opcode_set_delay_timer_equals_vx,
            re.compile(r'^F[0-9A-F]18$'): self.opcode_set_sound_timer_equals_vx,
            re.compile(r'^F[0-9A-F]1E$'): self.opcode_set_i_equals_i_plus_vx,
            re.compile(r'^F[0-9A-F]29$'): self.opcode_set_i_equals_sprite_location_in_vx,
            re.compile(r'^F[0-9A-F]33$'): self.opcode_store_bcd_rep_of_vx,
            re.compile(r'^F[0-9A-F]55$'): self.opcode_store_registers_vzero_vx,
            re.compile(r'^F[0-9A-F]65$'): self.opcode_read_registers_vzero_vx_from_memory_i,
        }

    def decode_opcode(self):

        print("Decode Opcode")
        
        byte1 = self.emu.memory[self.emu.program_counter]
        byte2 = self.emu.memory[self.emu.program_counter + 1]
        opcode_string = "{:02x}{:02x}".format(byte1, byte2)
        opcode_upper = opcode_string.upper()

        self.emu.opcode = (byte1 << 8) | byte2
        
        print(f"THIS IS OPCODE: {self.emu.opcode}")
        
        self.emu.nibble = (self.emu.opcode >> 12) & 0xF
        self.emu.x_nibble = (self.emu.opcode >> 8) & 0xF
        self.emu.y_nibble = (self.emu.opcode >> 4) & 0xF
        self.emu.n_nibble = self.emu.opcode & 0xF
        self.emu.nn_nibble = self.emu.opcode & 0xFF
        self.emu.nnn_nibble = self.emu.opcode & 0x0FFF

        # Iterate over the dictionary and execute the corresponding function for the matched opcode
        for pattern, handler in self.opcode_regex_map.items():
            if pattern.match(opcode_upper):
                handler()  # Execute the opcode handling function
                break
            
    ####################################################################################################
         
    #####
    #   #
    #   #
    #   #
    #####
    
    def opcode_clear_screen(self):
        
        print("[0.E0] OPCODE: Clear Screen \n")
        
        self.emu.display = [[0 for _ in range(64)] for _ in range(32)]
        self.emu.program_counter += 2

    
    def opcode_ret(self):

        print("{0.EE}")
        
        # Check if stack is not empty
        if len(self.emu.stack) > 0:
            # Get the top element from the stack
            pc = self.emu.stack.pop()

            # Set the program counter to the value retrieved from the stack
            self.emu.program_counter = pc
            
        
    ####################################################################################################
        
      #
    # # 
      #  
      #
    ##### 
    
    def opcode_jump(self):
        
        print("[1] OPCODE: JMP \n")
        
        self.emu.program_counter = self.emu.nnn_nibble
    
    
    ####################################################################################################
    
    #####
        #
    #####
    #
    #####    

    def opcode_call(self):

        print("[2] OPCODE: ADD TO STACK & JMP \n")
        
        # Push the current value of the ProgramCounter + 2 onto the stack
        self.emu.stack.append(self.emu.program_counter + 2)

        # Set the value of the ProgramCounter to the value of nnn
        self.emu.program_counter = self.emu.nnn_nibble

    
    ####################################################################################################
    
    ######
         #
    ######
         #
    ######
    
    
    def opcode_skip_vx_equals_nn(self):
        
        print("[3] OPCODE: CMP VX = KK \n")
             
        if self.emu.registers[self.emu.x_nibble] == self.emu.nn_nibble:
            self.emu.program_counter += 4
        else:
            self.emu.program_counter += 2
    
    
    ####################################################################################################
    
    #   #
    #   #
    #####
        #
        #

    def opcode_skip_vx_not_equals_nn(self):
        
        print("[4] OPCODE: CMP VX != VY \n")
                    
        if self.emu.registers[self.emu.x_nibble] != self.emu.nn_nibble:
            self.emu.program_counter += 4
        else:
            self.emu.program_counter += 2

    
    ####################################################################################################
    
    #####
    #
    #####
        #
    #####
    
    def opcode_skip_vx_equals_vy(self):
        
        print("[5] OPCODE: CMP VX == VY \n")
                                
        if self.emu.registers[self.emu.x_nibble] == self.emu.registers[self.emu.y_nibble]:
            self.emu.program_counter += 4
        else:
            self.emu.program_counter += 2
    
    
    ####################################################################################################
    
    #####
    #
    #####
    #   #
    #####
    
    def opcode_set_vx_equals_nn(self):
        
        print("[6] OPCODE: VX = KK \n")
        
        #print(f'0x{self.emu.nn_nibble} or {int(self.emu.nn_nibble, 16)} is being copied into V{self.emu.x_nibble} \n')
        
        self.emu.registers[self.emu.x_nibble] = self.emu.nn_nibble
        self.emu.program_counter += 2

    
    ####################################################################################################

    #####
        #
       #
      #
     #
    
    def opcode_set_vx_plus_nn(self):
        
        print("[7] OPCODE: Adds the value kk to the value of register Vx, then stores the result in Vx. \n")
            
        a = self.emu.registers[self.emu.x_nibble]
        b = self.emu.nn_nibble
        
        result = a + b
                    
        result = result & 0xFF
        
        # print(f'{int_a} + {int_b} = {int_c} \n')
                                
        self.emu.registers[self.emu.x_nibble] = result
        
        self.emu.program_counter += 2


    ####################################################################################################

    #####
    #   #
    #####
    #   #
    #####
    
    def opcode_set_vx_equals_vy(self):
        
        print("[8.0] OPCODE: Set Vx = Vy. \n")
        
        print(f'V{self.emu.x_nibble} is being set to V{self.emu.y_nibble} \n')
        
        self.emu.registers[self.emu.x_nibble] = self.emu.registers[self.emu.y_nibble]
        self.emu.program_counter += 2
    

    #####       #      
    #   #     # #
    #####       #
    #   # ###   #
    ##### ### #####
    
    def opcode_set_vx_or_vy(self):

        print("[8.1] OPCODE: Set Vx = Vx OR Vy \n")
        
        int_a = self.emu.registers[self.emu.x_nibble]
        int_b = self.emu.registers[self.emu.y_nibble]
        
        int_c = int_a | int_b
        int_c = int_c & 0xFF
        
        # The AND, OR and XOR opcodes (8XY1, 8XY2 and 8XY3) reset the flags register to zero
        self.emu.registers[0xF] = 0
        
        self.emu.registers[self.emu.x_nibble] = int_c
        self.emu.program_counter += 2
    

    #####     #####   
    #   #         #
    #####     #####
    #   # ### #  
    ##### ### #####
    
    def opcode_set_vx_and_vy(self):
        
        print("[8.2] Set Vx = Vx AND Vy \n")     
        
        int_a = self.emu.registers[self.emu.x_nibble]
        int_b = self.emu.registers[self.emu.y_nibble]

        res = int_a & int_b
        res = res & 0xFF
        
        # The AND, OR and XOR opcodes (8XY1, 8XY2 and 8XY3) reset the flags register to zero
        self.emu.registers[0xF] = 0
        
        self.emu.registers[self.emu.x_nibble] = math.floor(res)
        self.emu.program_counter += 2
    

    #####     #####   
    #   #         #
    #####     #####
    #   # ###     #
    ##### ### #####
    
    def opcode_set_vx_xor_vy(self):
        
        print(f"[8.3] OPCODE: XOR Vx, Vy \n")

        int_a = self.emu.registers[self.emu.x_nibble]
        int_b = self.emu.registers[self.emu.y_nibble]
        
        int_c = int_a ^ int_b
        int_c = int_c & 0xFF
        
        # The AND, OR and XOR opcodes (8XY1, 8XY2 and 8XY3) reset the flags register to zero
        self.emu.registers[0xF] = 0
        
        self.emu.registers[self.emu.x_nibble] = int_c
        self.emu.program_counter += 2
    

    #####     #   #
    #   #     #   #
    #####     #####
    #   # ###     #
    ##### ###     #
    
    def opcode_set_vx_add_vy(self):

        print(f"[8.4] OPCODE: ADD Vx, Vy \n")
        
        a = self.emu.registers[self.emu.x_nibble]
        b = self.emu.registers[self.emu.y_nibble]
        
        result = a + b

        res = result & 0xFF
                        
        self.emu.registers[self.emu.x_nibble] = res
        
        # 8 bits is one byte
        if result > 255:
            self.emu.registers[0xF] = 1
        else:
            self.emu.registers[0xF] = 0
            
        self.emu.program_counter += 2
        

    #####     #####
    #   #     #    
    #####     #####
    #   # ###     #
    ##### ### #####
    
    def opcode_set_vx_sub_vy(self):
        
        print("{8.5} OPCODE: SUB \n")
        
        a = self.emu.registers[self.emu.x_nibble]
        b = self.emu.registers[self.emu.y_nibble]
                        
        result = a - b
        res = result & 0xFF
                        
        self.emu.registers[self.emu.x_nibble] = res
        
        print(f'{a} - {b} = {res} \n')
        
        if result > 0:
            self.emu.registers[0xF] = 1
            
        else:
            self.emu.registers[0xF] = 0
            
        self.emu.program_counter += 2
    

    #####     #####
    #   #     #    
    #####     #####
    #   # ### #   #
    ##### ### #####

    def opcode_set_vx_shr_vy(self):

        print("{8.6} \n")

        a = self.emu.registers[self.emu.x_nibble]
        b = self.emu.registers[self.emu.y_nibble]
        
        # // Get the least significant bit of the value in register Vx
        lsb = a & 0x1

        # Shift the value in register VX to the right by 1 bit.
        self.emu.registers[self.emu.x_nibble] >>= 1

        if lsb == 1:
            self.emu.registers[0xF] = 1
        else:
            self.emu.registers[0xF] = 0
            
        self.emu.program_counter += 2
    

    #####     #####
    #   #         #
    #####         #
    #   # ###     #
    ##### ###     #
    
    def opcode_set_vx_subn_vy(self):

        print("{8.7} OPCODE: SUBN \n")
        
        result = self.emu.registers[self.emu.y_nibble] - self.emu.registers[self.emu.x_nibble]

        self.emu.registers[self.emu.x_nibble] = result & 0xFF
        
        if result > 0:
            self.emu.registers[0xF] = 1
            
        else:
            self.emu.registers[0xF] = 0
            
        self.emu.program_counter += 2
    

    #####     #####
    #   #     #    
    #####     #####
    #   # ### #    
    ##### ### #####    

    def opcode_set_vx_shl_vy(self):
        
        print("[8.E] OPCODE: SHL Vx {, Vy} \n")

        self.emu.registers[self.emu.x_nibble] = self.emu.registers[self.emu.y_nibble]

        a = self.emu.registers[self.emu.x_nibble]
        
        # // Get the least significant bit of the value in register Vx
        msb = (a >> 7) & 0x1

        result = self.emu.registers[self.emu.x_nibble] << 1
        result = result & 0xFF

        # Shift the value in register VX to the right by 1 bit.
        self.emu.registers[self.emu.x_nibble] = result

        if msb == 1:
            self.emu.registers[0xF] = 1
        else:
            self.emu.registers[0xF] = 0
            
        self.emu.program_counter += 2
    

    ####################################################################################################
    
    #####
    #   #
    #####
        #
        #
    
    def opcode_set_vx_not_equals_vy(self):
        
        print("[9] OPCODE: SKIP IF VX != VY \n")
        
        #print(f'These are the values compared x_nibble: {self.emu.registers[f"V{self.emu.y_nibble}"]} and y_nibble: {self.emu.registers[f"V{self.emu.y_nibble}"]}')
                    
        if self.emu.registers[self.emu.x_nibble] != self.emu.registers[self.emu.y_nibble]:
            print('SKIP')
            self.emu.program_counter += 4
        else:
            print('NO SKIP')
            self.emu.program_counter += 2
    
    
    ####################################################################################################
    
    #####
    #   #
    #####
    #   #
    #   #
    
    def opcode_set_i_equals_nnn(self):
        
        print("[A] OPCODE: I IS SET TO NNN \n")
        
        #print(f'{int(self.emu.nnn_nibble, 16)} => {self.emu.index_register} = {int(self.emu.nnn_nibble, 16)} \n')
        
        self.emu.index_register = self.emu.nnn_nibble
        self.emu.program_counter += 2
    
    
    ####################################################################################################   
        
    ####
    #   #
    #####
    #   #
    ####

    
    def opcode_jump_nnn_plus_vzero(self):
        
        print(f"[B] JMP => NNN + V0 \n")
        
        res = self.emu.nnn_nibble + self.emu.registers[self.emu.x_nibble]
    
        self.emu.program_counter = res + 2
    
    
    ####################################################################################################
    
    #####
    #
    #
    #
    #####
    
    def opcode_randombyte_and_nn(self):
        
        print(f"[C] OPCODE: Vx = random byte AND kk \n")
                    
        rand_num = random.randrange(0, 255)

        res = rand_num & self.emu.nn_nibble

        res = res & 0xFF

        self.emu.registers[f'V{self.emu.x_nibble}'] = res
        
        self.emu.program_counter += 2
    
    
    ####################################################################################################
    
    #  #
    #   #
    #    #
    #   # 
    #  #
    
    def opcode_draw(self):
        
        print("{D} OPCODE: DRAW \n")

        self.emu.draw_begin = True
        
        
    ####################################################################################################
    
    ######     ##### ######
    #          #   # #
    ######     ##### ######
    #      ###     # #
    ###### ###     # ######
     
    def opcode_skip_if_key_in_vx(self):

        print("[F.9E] \n")
        
        if self.emu.key_pressed == self.emu.registers[self.emu.x_nibble]:
        
            self.emu.program_counter += 4
            
        else:
            
            self.emu.program_counter += 2
            
    
    ######     #####   ##
    #          #   #  # #
    ######     #####    #
    #      ### #   #    #
    ###### ### #   #  #####
    
    def opcode_skip_if_key_not_in_vx(self):

        print("{F.A1} OPCODE: Skip next instruction if key with the value of Vx is not pressed. \n")
            
        if self.emu.key_pressed != self.emu.registers[self.emu.x_nibble]:
        
            self.emu.program_counter += 4
            
        else:
            
            self.emu.program_counter += 2
            

    
    ####################################################################################################
            
    #####     ##### #####
    #         #   #     #
    #####     #   #     #
    #     ### #   #     #
    #     ### #####     #
    
    def opcode_set_vx_equals_delay_timer(self):
        
        print("{F.07} OPCODE: VX = DELAY TIMER \n")
        
        self.emu.registers[f'V{self.emu.x_nibble}'] = self.delay_timer
        self.emu.program_counter += 2
            
            
    #####     ##### #####
    #         #   # #   #
    #####     #   # #####
    #     ### #   # #   #
    #     ### ##### #   #
    
    def opcode_wait_keypress_store_vx(self):
        
        print("{F.0A} OPCODE: KEY PRESS => VX \n")

        def wait_for_keypress():
            while self.emu.key_pressed == -1:
                pass  

            # Key has been pressed
            self.emu.registers[self.emu.x_nibble] = self.emu.key_pressed
            self.emu.waiting_for_keypress = False
            self.emu.program_counter += 2

        if self.emu.key_pressed == -1:
            self.emu.waiting_for_keypress = True
            # Start a new thread to wait for keypress
            threading.Thread(target=wait_for_keypress).start()
    
    
    #####       ##   ##### 
    #          # #   #     
    #####        #   ##### 
    #     ###    #       # 
    #     ###  ##### ##### 
    
    def opcode_set_delay_timer_equals_vx(self):
        
        print("{F.15} OPCODE: DELAY TIMER \n")
        self.delay_timer = self.emu.registers[self.emu.x_nibble]
        self.emu.program_counter += 2

    
    #####       ##   ##### 
    #          # #   #   #
    #####        #   ##### 
    #     ###    #   #   # 
    #     ###  ##### ##### 
    
    def opcode_set_sound_timer_equals_vx(self):
        
        print("{F.18} OPCODE: SOUND_TIMER = Vx \n")
        
        self.sound_timer = self.emu.registers[self.emu.x_nibble]
        print(f'This is the sound_timer: {self.sound_timer}')
        
        self.emu.program_counter += 2
    
    
    #####       ##   ##### 
    #          # #   #   
    #####        #   ##### 
    #     ###    #   #    
    #     ###  ##### ##### 
    
    def opcode_set_i_equals_i_plus_vx(self):
        
        print("{F.1E} OPCODE: I = I + VX \n")

        int_a = self.emu.registers[self.emu.x_nibble]
        int_b = self.emu.index_register
        
        res = int_a + int_b
        
        print(f'{self.emu.index_register} + {self.emu.registers[self.emu.x_nibble]} = {res} \n')

        self.emu.index_register = res
                        
        self.emu.program_counter += 2
    
    
    #####      ##### ##### 
    #              # #   #
    #####      ##### ##### 
    #     ###  #         # 
    #     ###  #####     # 
    
    def opcode_set_i_equals_sprite_location_in_vx(self):
                
        print("[F.29] OPCODE: Set I = location of sprite for digit Vx.")
        
        offsets = [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75 ]

        self.emu.index_register = 0x50 + offsets[self.emu.registers[self.emu.x_nibble]]
        
        self.emu.program_counter += 2
    
    
    #####      ##### ##### 
    #              #     #
    #####      ##### ##### 
    #     ###      #     # 
    #     ###  ##### ##### 
    
    def opcode_store_bcd_rep_of_vx(self):
        
        print("{F.33} OPCODE: BCD REP")
                        
        self.emu.memory[self.emu.index_register] = self.emu.registers[self.emu.x_nibble] // 100
        self.emu.memory[self.emu.index_register+1] = (self.emu.registers[self.emu.x_nibble] // 10) % 10
        self.emu.memory[self.emu.index_register+2] = self.emu.registers[self.emu.x_nibble] % 10
        
        self.emu.program_counter += 2
        
        
    #####      ##### ##### 
    #          #     #    
    #####      ##### ##### 
    #     ###      #     # 
    #     ###  ##### ##### 
    
    def opcode_store_registers_vzero_vx(self):

        print("{F.55}")
        
        for i in range(self.emu.x_nibble + 1):
            self.emu.memory[self.emu.index_register+i] = self.emu.registers[i]
  
        # The save and load opcodes (FX55 and FX65) increment the index register
        self.emu.index_register += 2
        self.emu.program_counter += 2
    
    
    #####      ##### ##### 
    #          #     #    
    #####      ##### ##### 
    #     ###  #   #     # 
    #     ###  ##### ##### 
    
    def opcode_read_registers_vzero_vx_from_memory_i(self):
        
        print("{F.65} OPCODE: READ V0->VX at I+X COPY => V0->VX")

        for i in range(self.emu.x_nibble + 1):
            self.emu.registers[i] = self.emu.memory[self.emu.index_register+i]
  
        # The save and load opcodes (FX55 and FX65) increment the index register 
        self.emu.index_register += 2
        self.emu.program_counter += 2