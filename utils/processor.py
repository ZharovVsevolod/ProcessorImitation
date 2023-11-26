class ProcessorImitation():
    """Класс для реализации модели процессорного ядра программно-аппаратного комплекса
    Parameters
    ----------
    register_size : int
        Количество регистров, которые могут использоваться в представителе класса
    
    Attributes
    ----------
    REG : list[int]
        Регистры, которые хранят данные
    CMEM : list[int]
        Память команд
    pc : int
        Счётчик команд
    
    Methods
    ----------
    set_command(cmd : int | list[int])
        Помещение команды в память команд
    
    delimeter_command(cmd : int)
        Функция для разделения входной закодированной команды
    
    command_loop(need_print : bool = True):
        Функция для последовательного применения команд
    
    clean_cmem( : )
        Сбрасывает все команды
    
    clean_reg( : )
        Сбрасывает значения регистров в ноль
    """
    def __init__(self, register_size:int, data_memory:list[int]|int=4, comand_memory = None) -> None:
        self.REG = []
        for _ in range(register_size):
            self.REG.append(0)
        
        if type(data_memory) is int:
            self.DMEM = []
            for _ in range(data_memory):
                self.DMEM.append(0)
        else:
            self.DMEM = data_memory
        if comand_memory is None:
            self.CMEM = []
        else:
            self.CMEM = comand_memory
        
        print(self.DMEM)

        # Счётчик команд
        self.pc = None

        # Секция флагов
        self.sf = 0 # Флаг знака результата операции (после сложения или вычитания)
        self.zf = 0 # Флаг нулевого результата операции (после сложения или вычитания)
    
    def set_command(self, cmd:int | list[int]) -> None:
        """Помещение команды в память команд
        Parameters
        ----------
        cmd : int | list[int]
            Команда, поступившая на вход. Может быть как одним значением, так и массивом сразу нескольких команд  
            В двочином виде она выглядит примерно следующим образом:  
            CCCCLLLLLLLLDDDDXXXXYYYY,  
            где CCCC - это тип команды (cmdtype);  
                LLLLLLLL - literal, используется, если необходимо взять конретное значение не из памяти регистров;  
                DDDD - номер регистра, в который надо записать результат (dest);  
                XXXX - номер регистра, где лежит значение первого операнда (op1);  
                YYYY - номер регистра, где лежит значение второго операнда (op2).  
        
        Raises
        ----------
        TypeError
            Если cmd не является int или list[int]
        """
        if type(cmd) == int:
            self.CMEM.append(cmd)
        elif type(cmd) == list:
            for command in cmd:
                if type(command) == int:
                    self.CMEM.append(command)
                else:
                    raise TypeError("В массиве не значение int", type(command))
        else:
            raise ValueError("Неправильный вид команды, он не int и не list[int]", type(cmd))
    
    def delimeter_command(self, cmd:int) -> int:
        """Функция для разделения входной закодированной команды
        Parameters
        ----------
        cmd : int
            Команда, поступившая на вход. В двочином виде она выглядит примерно следующим образом:
            CCCCLLLLLLLLDDDDXXXXYYYY,  
            где CCCC - это тип команды (cmdtype);  
                LLLLLLLL - literal, используется, если необходимо взять конретное значение не из памяти регистров;  
                DDDD - номер регистра, в который надо записать результат (dest);  
                XXXX - номер регистра, где лежит значение первого операнда (op1);  
                YYYY - номер регистра, где лежит значение второго операнда (op2).  
        
        Returns
        ----------
        cmdtype : int
            Тип команды
        literal : int
            Конкретное значение числа не из памяти регистров
        dest : int
            Номер регистра, в который надо записать результат
        op1 : int
            Номер регистра, где лежит значение первого операнда
        op2 : int
            Номер регистра, где лежит значение второго операнда
        
        Raises
        ----------
        ValueError
            Если cmd не соответсвует требованиям. Она должна иметь вид CCCC00000000DDDDXXXXYYYY в побитовом виде
        """
        # Проверка
        if cmd > 0xFFFFFFFF:
            raise ValueError("Команда не соответсвует требованиям. Она должна иметь вид CCCC00000000DDDDXXXXYYYY", "{0:032b}".format(cmd))

        operand_2 = cmd & 15
        operand_1 = (cmd >> 4) & 15
        dest = (cmd >> 8) & 15
        literal = (cmd >> 12) & 255
        cmdtype = (cmd >> 28) & 15

        return cmdtype, literal, dest, operand_1, operand_2
    
    def command_loop(self, need_print:bool = True) -> None:
        """Функция для последовательного применения команд
        Parameters
        ----------
        need_print : bool = True
            Необходим ли после каждой команды вывод подобного описания команды и результат её выполнения (значения регистров). 
            По умолчанию True
        """
        N = len(self.CMEM)
        self.pc = 0
        while self.pc < N:
            if need_print:
                print(self.REG)
            cmd = self.CMEM[self.pc]
            cmdtype, literal, dest, op1, op2 = self.delimeter_command(cmd)
            self.command(cmdtype=cmdtype, operand_1=op1, operand_2=op2, literal=literal)
            if need_print:
                self.print_command(cmdtype=cmdtype, operand_1=op1, operand_2=op2, literal=literal)
                print(self)
                print()
    
    def set_flags(self, result:int):
        if result == 0:
            self.zf = 1
            self.sf = 0
        elif result > 0:
            self.zf = 0
            self.sf = 0
        else:
            self.zf = 0
            self.sf = 1
    
    def command(self, cmdtype:int, operand_1:int, operand_2:int, literal:int) -> None:
        match cmdtype:
            case 0: # MOV, перемещение данных из одного регистра в другой
                self.REG[operand_1] = self.REG[operand_2]
            case 1: # MOV, перемещение (установка) из literal (определённого значения) в регистр
                self.REG[operand_1] = literal
            case 2: # MOV, перемещение данных из памяти данных в память регистра
                self.REG[operand_1] = self.DMEM[operand_2]
            case 3: # MOV, перемещение данных из памяти регистра в память данных
                self.DMEM[operand_1] = self.REG[operand_2]
            case 4: # XCHG, поменять содержимое операндов местами
                self.REG[operand_1], self.REG[operand_2] = self.REG[operand_2], self.REG[operand_1]
            case 5: # ADD, сложение операндов
                self.REG[operand_1] = self.REG[operand_1] + self.REG[operand_2]
                self.set_flags(self.REG[operand_1])
            case 6: # ADD, сложение операнда с определённым числом
                self.REG[operand_1] = self.REG[operand_1] + literal
                self.set_flags(self.REG[operand_1])
            case 7: # SUB, вычитание операндов
                self.REG[operand_1] = self.REG[operand_1] - self.REG[operand_2]
                self.set_flags(self.REG[operand_1])
            case 8: # SUB, вычитание из операнда числа
                self.REG[operand_1] = self.REG[operand_1] - literal
                self.set_flags(self.REG[operand_1])
            case 9: # CMP, сравнение, вычитание без записи (для флага) операнда
                temp = self.REG[operand_1] - self.REG[operand_2] # SF = 1: op1 < op2, SF = 0: op1 > op2
                self.set_flags(temp)
            case 10: # CMP, сравнение, вычитание без записи (для флага) числа
                temp = self.REG[operand_1] - literal # SF = 1: op1 < literal, SF = 0: op1 > literal
                self.set_flags(temp)
            case 11: # JS прыжок при SF = 1 (т.е. последнее арифметическое действие =< 0)
                if self.sf == 1:
                    self.pc = literal - 1 # -1, потому что в конце функции self.pc + 1
            case 12: # JNS прыжок при SF = 0 (т.е. последнее арифметическое действие >= 0)
                if self.sf == 0:
                    self.pc = literal - 1 # -1, потому что в конце функции self.pc + 1
            case 13: # JNE прыжок при ZF = 0 (т.е. последнее арифметическое действие != 0)
                if self.zf == 0:
                    self.pc = literal - 1 # -1, потому что в конце функции self.pc + 1
            case 14: # MOV rx, [rx], в регистре лежит адрес для данных
                self.REG[operand_1] = self.DMEM[self.REG[operand_2]]
            case 15: # JE прыжок при ZF = 1 (т.е. последнее арифметическое действие = 0)
                if self.zf == 1:
                    self.pc = literal - 1 # -1, потому что в конце функции self.pc + 1
            case _:
                raise ValueError("Неизвестная команда")
        self.pc += 1
    
    def print_command(self, cmdtype:int, operand_1:int, operand_2:int, literal:int) -> None:
        match cmdtype:
            case 0: # MOV, перемещение данных из одного регистра в другой
                print(f"MOV, REG[{operand_1}] <- REG[{operand_2}]")
            case 1: # MOV, перемещение (установка) из literal (определённого значения) в регистр
                print(f"MOV, REG[{operand_1}] <- {literal}")
            case 2: # MOV, перемещение данных из памяти данных в память регистра
                print(f"MOV, REG[{operand_1}] <- DMEM[{operand_2}]")
            case 3: # MOV, перемещение данных из памяти регистра в память данных
                print(f"MOV, DMEM[{operand_1}] <- REG[{operand_2}]")
            case 4: # XCHG, поменять содержимое операндов местами
                print(f"XCHG, REG[{operand_1}] <-> REG[{operand_2}]")
            case 5: # ADD, сложение операндов
                print(f"ADD, REG[{operand_1}] <- REG[{operand_1}] + REG[{operand_2}]")
            case 6: # ADD, сложение операнда с определённым числом
                print(f"ADD, REG[{operand_1}] <- REG[{operand_1}] + {literal}")
            case 7: # SUB, вычитание операндов
                print(f"SUB, REG[{operand_1}] <- REG[{operand_1}] - REG[{operand_2}]")
            case 8: # SUB, вычитание из операнда числа
                print(f"SUB, REG[{operand_1}] <- REG[{operand_1}] - {literal}")
            case 9: # CMP, сравнение, вычитание без записи (для флага) операнда
                print(f"CMP, REG[{operand_1}] - REG[{operand_2}]")
            case 10: # CMP, сравнение, вычитание без записи (для флага) числа
                print(f"CMP, REG[{operand_1}] - {literal}")
            case 11: # JS прыжок при SF = 1 (т.е. последнее арифметическое действие =< 0)
                print(f"JS прыжок при SF = 1 в команду {literal}")
            case 12: # JNS прыжок при SF = 0 (т.е. последнее арифметическое действие >= 0)
                print(f"JNS прыжок при SF = 0 в команду {literal}")
            case 13: # JNE прыжок при ZF = 0 (т.е. последнее арифметическое действие != 0)
                print(f"JNE прыжок при ZF = 0 в команду {literal}")
            case 14: # JG прыжок при SF = 0 и ZF = 0 (т.е. последнее арифметическое действие < 0)
                print(f"MOV, REG[{operand_1}] <- DMEM[REG[{operand_2}]]")
            case 15: # JE прыжок при ZF = 1 (т.е. последнее арифметическое действие = 0)
                print(f"JE прыжок при ZF = 1 в команду {literal}")
            case _:
                raise ValueError("Неизвестная команда")
        

    def command_old(self, cmdtype:int, operand_1:int, operand_2:int, destination:int, literal:int) -> None:
        """Выбор и выполнение команды  
        Данная команда записывает в нужный регистр результат выполнения команды и обновляет счётчик команд pc
        Parameters
        ----------
        cmdtype : int
            Тип команды. Допускаются следующие значения:  
                0 - сложение;  
                1 - вычитание;  
                2 - побитовое И;  
                3 - побитовое ИЛИ;  
                4 - побитовое НЕ;  
                5 - битовый сдвиг на один шаг вправо;  
                6 - битовый сдвиг на один шаг влево;  
                7 - возведение в степень;  
                8 - поиск максимума;  
                9 - возвращение значения literal;  
                10 - безусловный переход jump через literal;  
                11 - условный переход при op1 == op2;  
                12 - условный переход при op1 != op2.  
        
        operand_1 : int
            Номер регистра, в котором лежит значение первого операнда
        
        operand_2 : int
            Номер регистра, в котором лежит значение второго операнда
        
        destination : int
            Номер регистра, в который необходимо записать получившееся значение

        literal : int
            Дополнительный операнд  
        
        Raises
        ----------
        ValueError
            Если значение cmdtype не будет принадлежать одному из перечисленных значений
        """
        op1 = self.REG[operand_1]
        op2 = self.REG[operand_2]

        match cmdtype:
            case 0:
                self.REG[destination] = op1 + op2
            case 1:
                self.REG[destination] = op1 - op2
            case 2:
                self.REG[destination] = op1 & op2
            case 3:
                self.REG[destination] = op1 | op2
            case 4:
                self.REG[destination] = ~op1
            case 5:
                self.REG[destination] = op1 >> 1
            case 6:
                self.REG[destination] = op1 << 1
            case 7:
                self.REG[destination] = op1 ^ op2
            case 8:
                self.REG[destination] = op1 if op1 > op2 else op2
            case 9:
                self.REG[destination] = literal
            case 10:
                self.pc = literal - 1
            case 11:
                self.pc = literal - 1 if op1 == op2 else self.pc
            case 12:
                self.pc = literal - 1 if op1 != op2 else self.pc
            case _:
                raise ValueError("Неизвестная команда")
        self.pc += 1
    
    def clean_cmem(self) -> bool:
        """Сбрасывает все команды"""
        self.CMEM = []
        return True
    
    def clean_reg(self) -> bool:
        """Сбрасывает значения регистров в ноль"""
        for i in range(len(self.REG)):
            self.REG[i] = 0
        return True
    
    def __repr__(self) -> str:
        return "".join([
            "Память регистров:\n", str(self.REG), 
            "\nПамять данных:\n", str(self.DMEM), 
            "\nПамять флагов:\nSF = ", str(self.sf), ", ZF = ", str(self.zf), 
            "\nСчётчик команд PC = ", str(self.pc)
        ])

def delimer_command(cmd:int) -> int:
    """Функция для разделения входной закодированной команды
    Parameters
    ----------
    cmd : int
        Команда, поступившая на вход. В двочином виде она выглядит примерно следующим образом:
        CCCCLLLLLLLLDDDDXXXXYYYY,  
        где CCCC - это тип команды (cmdtype);  
            LLLLLLLL - literal, используется, если необходимо взять конретное значение не из памяти регистров;  
            DDDD - номер регистра, в который надо записать результат (dest);  
            XXXX - номер регистра, где лежит значение первого операнда (op1);  
            YYYY - номер регистра, где лежит значение второго операнда (op2).  
    
    Returns
    ----------
    cmdtype : int
        Тип команды
    literal : int
        Конкретное значение числа не из памяти регистров
    dest : int
        Номер регистра, в который надо записать результат
    op1 : int
        Номер регистра, где лежит значение первого операнда
    op2 : int
        Номер регистра, где лежит значение второго операнда
    
    Raises
    ----------
    ValueError
        Если cmd не соответсвует требованиям. Она должна иметь вид CCCC00000000DDDDXXXXYYYY в побитовом виде
    """
    # Проверка
    if cmd > 0xFFFFFFFF:
        raise ValueError("Команда не соответсвует требованиям. Она должна иметь вид CCCC00000000DDDDXXXXYYYY", "{0:032b}".format(cmd))

    op2 = cmd & 15
    op1 = (cmd >> 4) & 15
    dest = (cmd >> 8) & 15
    literal = (cmd >> 12) & 31
    cmdtype = (cmd >> 28) & 15

    return cmdtype, literal, dest, op1, op2

def command_type_description(cmdtype:int) -> str:
    """Возвращение типа команды
    Parameters
    ----------
    cmdtype : int
        Тип команды. Допускаются следующие значения:  
            0 - сложение;  
            1 - вычитание;  
            2 - побитовое И;  
            3 - побитовое ИЛИ;  
            4 - побитовое НЕ;  
            5 - битовый сдвиг на один шаг вправо;  
            6 - битовый сдвиг на один шаг влево;  
            7 - возведение в степень;  
            8 - поиск максимума;  
            9 - возвращение значения literal;  
            10 - безусловный переход jump через literal;  
            11 - условный переход при op1 == op2;  
            12 - условный переход при op1 != op2.  
    
    Returns
    ----------
    str
        Тип команды
    
    Raises
    ----------
    ValueError
        Если значение cmdtype не будет принадлежать одному из перечисленных значений
    """
    match cmdtype:
        case 0:
            return "сложение"
        case 1:
            return "вычитание"
        case 2:
            return "побитовое И"
        case 3:
            return "побитовое ИЛИ"
        case 4:
            return "побитовое НЕ"
        case 5:
            return "битовый сдвиг на один шаг вправо"
        case 6:
            return "битовый сдвиг на один шаг влево"
        case 7:
            return "возведение в степень"
        case 8:
            return "поиск максимума"
        case 9:
            return "указание literal значения"
        case 10:
            return "безусловный переход jump через literal"
        case 11:
            return "условный переход при op1 == op2"
        case 12:
            return "условный переход при op1 != op2"
        case _:
            raise ValueError("Неизвестная команда") 

def print_command(cmd:int) -> None:
    """Вывод команды с разделением на части
    Parameters
    ----------
    cmd : int
        Команда, поступившая на вход. В двочином виде она выглядит примерно следующим образом:
        CCCC00000000DDDDXXXXYYYY,  
        где CCCC - это тип команды (cmdtype),  
            DDDD - номер регистра, в который надо записать результат (dest),  
            XXXX - номер регистра, где лежит значение первого операнда (op1),  
            YYYY - номер регистра, где лежит значение второго операнда (op2).  
        Нулями указаны разряды, которые в данной работе не используются (их значение будет записано в переменную literal)
    
    Raises
    ----------
    ValueError
        Если cmd не соответсвует требованиям. Она должна иметь вид CCCC00000000DDDDXXXXYYYY в побитовом виде
    ValueError
        Если значение cmdtype не будет принадлежать одному из возможных значений
    """
    cmdtype, literal, dest, op1, op2 = delimer_command(cmd)
    print(f"cmdtype = {cmdtype}, {command_type_description(cmdtype)}")
    print(f"literal = {literal}")
    print(f"dest = {dest}")
    print(f"op1 = {op1}")
    print(f"op2 = {op2}")