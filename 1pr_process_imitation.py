from utils.processor import ProcessorImitation

DATA = [1, 2, 3, 4]
comands = [
        # Заполнение памяти регистров значениями
        0x20000000, # 0 MOV from data memory
        0x20000010, # 1 MOV from data memory
        0x20000020, # 2 MOV from data memory
        0x20000030, # 3 MOV from data memory
        # Суммы и разности
        0x50000031, # 4 ADD 
        0x6000A000, # 5 ADD
        0x70000030, # 6 SUB
        # Сравнения
        0x90000030, # 7 CMP
        0x90000023, # 8 CMP
        # Поиск максимума 1
        0x90000030, # 9 CMP
        0xB000D000, # 10 JS (A)
        0x00000033, # 11 MOV (op1 = max) (B)
        0xC000E000, # 12 JNS (C)
        0x00000030, # 13 MOV (op2 = max) (D)
        # Поиск максимума 2
        0x90000021, # 14 CMP (E)
        0xB0012000, # 15 JS (F)
        0x00000022, # 16 MOV (op1 = max) (10)
        0xC0013000, # 17 JNS (11)
        0x00000021, # 18 MOV (op2 = max) (12)
        # Поиск максимума 3
        0x90000010, # 19 CMP (13)
        0xB0016000, # 20 JS (14)
        0xC0017000, # 21 JNS (15)
        0x00000010, # 22 MOV (op2 = max) (16)
        # Поиск максимума 4
        0x90000012, # 23 CMP (17)
        0xB001A000, # 24 JS (18)
        0xC001B000, # 25 JNS (19)
        0x00000012, # 26 MOV (op2 = max) (1A)
]


process = ProcessorImitation(4, DATA, comand_memory=comands)


process.command_loop()