import re

class AssemblerConversion():
    def __init__(self):
        self.CMEM = []

        # Область хранения обработки команды
        self.command_type = None
        self.type_of_memory_dest = None
        self.memory_number_dest = None
        self.type_of_memory_in = None
        self.memory_number_in = None
        self.literal = None
        self.extra_pin = None

        self.pc = None
        self.point_dict = {}
        self.jump_dict = {}
        self.jump_pc = {}

        self.loop_repeat = None
        self.some_massive = []

        self.converse_list = []
        
    def converse_all(self, cmd:list[str], debug_print=False):
        converse_list = []
        self.pc = 0
        for command in cmd:
            temp = self.converse(command, debug_print)
            if temp != -2:
                self.converse_list.append(temp)
                self.pc += 1
        
        # Заполнение кодами для команд типа jump с метками
        self.converse_list = self.fill_jumps(self.converse_list)
        return self.converse_list
    
    def converse(self, cmd:str, debug_print=False):
        # Лексический анализ
        cmd_split = self.split_command(cmd)
        if debug_print:
            print(cmd_split)

        # Проверка и представление в числах
        self.transform_command(cmd_split)
        if debug_print:
            self.print_inner()
        
        # Генератор кода
        m_command = self.to_command()

        self.clear_inner()
        return m_command
    
    def fill_jumps(self, m_command):
        for i in range(len(m_command)):
            if m_command[i] == -1:
                type_jump = self.jump_pc[i]
                name_point = self.jump_dict[i]
                number_point = self.point_dict[name_point]
                self.literal = number_point
                m_command[i] = self.make_jump(type_jump)
        
        return m_command
    
    def make_jump(self, type_of_jump):
        match type_of_jump:
            case "js":
                cmdtype = 0xB0000000
            case "jns":
                cmdtype = 0xC0000000
            case "je":
                cmdtype = 0xF0000000
            case "jne":
                cmdtype = 0xD0000000
        
        literal, op2 = self.standart_literal()
        dest = 0x00000000
        op1 = 0x00000000

        out_command = cmdtype + literal + dest + op1 + op2
        return out_command

    def split_command(self, cmd:str) -> list[str]:
        return list(filter(None, re.split(pattern="[ ,:]", string=cmd)))
    
    def split_attribute(self, attr:list) -> (str, int):
        if attr[0] == "[":
            dest = attr[1]
            number = attr[2:-1]
            self.extra_pin = 2
            return dest, int(number)
        else:
            dest = attr[0]
            number = attr[1:]
            return dest, int(number)
    
    def transform_command(self, command:list) -> list:
        if len(command) == 3: # Стандартная обработка команды, которая выглядит как "<команда> <операнд 1>, <операнд 2>"
            self.command_type = command[0]
            if self.command_type in ["mov", "cmp", "add", "sub"]:
                self.type_of_memory_dest, self.memory_number_dest = self.split_attribute(command[1])
                try:
                    self.literal = int(command[2])
                    self.extra_pin = 0
                except ValueError:
                    self.type_of_memory_in, self.memory_number_in = self.split_attribute(command[2])
                    if self.extra_pin is None:
                        self.extra_pin = 1
                
            elif self.command_type == "xchg":
                self.type_of_memory_dest, self.memory_number_dest = self.split_attribute(command[1])
                self.type_of_memory_in, self.memory_number_in = self.split_attribute(command[2])
            
            else:
                raise ValueError("Не существует команды", self.command_type)
        else: # Если у нас не 3 элемента, а 2 или 4, то тут присутсвует прыжки или ссылки соответственно, нужна другая обработка
            if len(command) == 2: # Обработка JS XXXX, где XXXX - это называние любой ссылки (например, L1)
                self.command_type = command[0]
                self.jump_dict[self.pc] = command[1]
                self.jump_pc[self.pc] = self.command_type
            elif len(command) == 4: # Обработка ссылки с командой, например, L1: add r0, r2
                self.point_dict[command[0]] = self.pc
                self.transform_command(command[1:])
            else:
                if command[0] == "set":
                    self.command_type = command[0]
                    massive = command[1:]
                    massive[0] = massive[0][1:]
                    massive[-1] = massive[-1][:-1]
                    self.some_massive = massive
                else:
                    raise ValueError("Не правильная команда, слишком много переменных. Их может быть от 1 до 4, а у вас = ", len(command))
    
    def set_data(self):
        print(self.some_massive)
        commands = []
        for i in range(len(self.some_massive)):
            commands.append(f"mov r0, {self.some_massive[i]}")
            commands.append(f"mov d{i}, r0")
        
        commands.append("mov r0, 0")
        print(commands)
        return commands
      
    def make_literal_number_from_10_to_16(self, literal):
        if literal > 0xFFFF and literal < 0:
            raise ValueError("Слишком большое число", literal)
        return "{0:04x}".format(literal)
    
    def number_10_to_16(self, num):
        if num > 15 and num < 0:
            raise ValueError("Неверный адрес операнда", num)
        return "{0:01x}".format(num)
    
    def standart_literal(self):
        literal_num = self.make_literal_number_from_10_to_16(self.literal)
        literal = int(f"0x0{literal_num}000", base=16)
        op2 = 0x00000000
        return literal, op2
    
    def standart_operand(self):
        literal = 0x00000000
        in_num = self.number_10_to_16(self.memory_number_in)
        op2 = int(f"0x000000{in_num}", base=16)
        return literal, op2
    
    def to_command(self):
        if self.command_type in ["js", "jns", "jne", "je"]:
            return -1
        
        if self.command_type == "set":
            coms = self.set_data()
            self.converse_all(cmd=coms)
            return -2
        
        match self.command_type:
            case "mov":
                if self.extra_pin == 0: # Значение literal
                    cmdtype = 0x10000000
                    literal, op2 = self.standart_literal()
                elif self.extra_pin == 1: # Из какой-то памяти, REG или DMEM
                    if self.type_of_memory_dest == "r" and self.type_of_memory_in == "r":
                        cmdtype = 0x00000000
                    elif self.type_of_memory_dest == "r" and self.type_of_memory_in == "d":
                        cmdtype = 0x20000000
                    elif self.type_of_memory_dest == "d" and self.type_of_memory_in == "r":
                        cmdtype = 0x30000000
                    literal, op2 = self.standart_operand()
                elif self.extra_pin == 2: # В регистре лежит ссылка на память в данных
                    cmdtype = 0xE0000000
                    literal, op2 = self.standart_operand()
            
            case "cmp":
                if self.extra_pin == 0: # Значение literal
                    cmdtype = 0xA0000000
                    literal, op2 = self.standart_literal()
                else:
                    cmdtype = 0x90000000
                    literal, op2 = self.standart_operand()
            
            case "add":
                if self.extra_pin == 0: # Значение literal
                    cmdtype = 0x60000000
                    literal, op2 = self.standart_literal()
                else:
                    cmdtype = 0x50000000
                    literal, op2 = self.standart_operand()
            
            case "sub":
                if self.extra_pin == 0: # Значение literal
                    cmdtype = 0x80000000
                    literal, op2 = self.standart_literal()
                else:
                    cmdtype = 0x70000000
                    literal, op2 = self.standart_operand()
            
            case "xchg":
                cmdtype = 0x40000000
                literal, op2 = self.standart_operand()
            
        dest = 0x00000000
        op1_num = self.number_10_to_16(self.memory_number_dest)
        op1 = int(f"0x00000{op1_num}0", base=16)

        out_command = cmdtype + literal + dest + op1 + op2
        return out_command
    
    def print_inner(self):
        print(f"command_type = {self.command_type}")
        print(f"type_of_memory_dest = {self.type_of_memory_dest}")
        print(f"memory_number_dest = {self.memory_number_dest}")
        print(f"type_of_memory_in = {self.type_of_memory_in}")
        print(f"memory_number_in = {self.memory_number_in}")
        print(f"literal = {self.literal}")
        print(f"extra_pin = {self.extra_pin}")
    
    def clear_inner(self):
        self.command_type = None
        self.type_of_memory_dest = None
        self.memory_number_dest = None
        self.type_of_memory_in = None
        self.memory_number_in = None
        self.literal = None
        self.extra_pin = None
        self.some_massive = []