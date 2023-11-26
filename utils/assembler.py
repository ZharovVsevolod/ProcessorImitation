import re
from typing import Literal

class AssemblerConversion():
    """Класс для реализации конверсии из программы на самоопределённом языке ассемблера в программу на машинном коде

    Поддерживает следующие типы команд:
    - `mov`: команда переноса в регистр (или в память данных) некоторое числовое значение, которое может быть как
            отдельным числом, так и значением в регистре, памяти данных или ссылкой на адрес.
            Примеры:
            - `mov r0 r1` - перенос в регистр с адресом 0 значения из регистра с адресом 1
            - `mov r0 d3` - перенос в регистр с адресом 0 значения из памяти данных с адресом 3
            - `mov d1 r12` - перенос в память данных с адресом 1 значения из регистра с адресом 12
            - `mov r4 17` - перенос в регистр с адресом 4 конкретного числового значения 17
            - `mov r2 [r0]` - перенос в регистр с адресом 4 значения из памяти данных с адресом, указанным в регистре с адресом 0
    - `set`: команда записи памяти данных. В память данных записывается массив, который указан после комадны `set`. 
            `Обязательно` первым элементов массива должна быть его длина (без этого первого числа). 
            Примеры:
            - `set [3, 1, 2, 3]` - запись в память данных массива [3, 1, 2, 3]. Первое число 3 указывает на количество данных в массиве
            - `set [8, 8, 7, 6, 5, 4, 3, 2, 1]` - запись в память данных массива [8, 8, 7, 6, 5, 4, 3, 2, 1]. Первое число 8 указывает на количество данных в массиве
    - `xchg`: поменять содержимое операндов местами. Поддерживает только работу с регистрами. 
            Примеры:
            - `xchg r0 r3` - содержимое регистров с адресами 0 и 3 меняются местами
            - `xchg r12 r7` - содержимое регистров с адресами 12 и 7 меняются местами
    - `add`: сложение числа, записаное в регистре, с числом из другого регистра или с явно указаным числом.
            Примеры:
            - `add r7 r0` - прибавить к числу, записанному в регистре с адресом 7, число, записанное в регистре с адресом 0
            - `add r5 123` - прибавить к числу, записанному в регистре с адресом 5, число 123
    - `sub`: вычитание из числа, записаное в регистре, числа из другого регистра или явно указаного числа.
            Примеры:
            - `sub r4 r3` - вычесть из числа, записанного в регистре с адресом 4 число, записанное в регистре с адресом 3
            - `sub r2 15` - вычесть из числа, записанного в регистре с адресом 2, число 15
    - `cmp`: сравнение числа из регистра с другим числом из регистра или явно указанным числом (влияет на флаги арифметических операций).
            Примеры:
            - `cmp r0 r1` - сравнить число из регистра с адресом 0 с числом из регистра с адресом 1
            - `cmp r0 5` - сравнить число из регистра с адресом 0 с числом 5
    - `js`, `jns`, `je`, `jne` прыжки: прыжки на указанную до или после прыжка определённую метку.
            Прыжки имеют следующие характеристики:
            - `js`: при `SF` = 1 (т.е. последнее арифметическое действие <= 0)
            - `jns`: при `SF` = 0 (т.е. последнее арифметическое действие >= 0)
            - `je`: при `ZF` = 1 (т.е. последнее арифметическое действие = 0)
            - `jne`: при `ZF` = 0 (т.е. последнее арифметическое действие != 0)

            `Обязательно` наличие метки в программе, куда прыжок будет осуществлён.

            Примеры прыжков:
            
            `js lama` - прыжок `js` в метку `lama`

            `jne vampire` - прыжок `jne` в метку `vampire`

            Примеры меток:
            
            `lama: mov r0 d3` - метка `lama`, которая ведёт на команду `mov r0 d3`

            `vampire: cmp r3 r0` - метка `vampire`, которая ведёт на команду `cmp r3 r0`
    
    Attributes
    ----------
    `command_type` : str = None
        Тип комады, которая обрабатывается в данный момент
    
    `type_of_memory_dest` : str = None
        Данные какого типа (`r` для регистров, `d` для данных) будут использоваться в качестве первого операнда

    `memory_number_dest` : int
        Адрес данных первого операнда
    
    `type_of_memory_in` : str
        Данные какого типа (`r` для регистров, `d` для данных) будут использоваться в качестве второго операнда

    `memory_number_in` : int
        Адрес данных второго операнда

    `literal` : int
        Дополнительное значение literal для чисел

    `extra_pin` : int
        Внутреняя переменная для обработки

    `pc` : int
        Счётчик команд

    `point_dict` : dictionary
        Словарь для меток, какой номер команды соответствует каждой метки

    `jump_dict` : dictionary
        Словарь для команд прыжков, какой тип прыжка был в команде

    `jump_pc` : dictionary
        Словарь для меток и команд прыжков, какая метка соответствует какому прыжку
    
    `some_massive` : list
        Дополнительная переменная для обработки команды set, куда записывается программа на ассемблере для установки памяти данных

    `converse_list` : list
        Переменная, где в результате обработки команд будет хранится программа, список из машинных кодов для `ProcessorImitation`
    
    Methods
    -------
    `converse_all`(cmd : list[str], debug_print : bool = False) -> list[int]
        Метод для перевода программы на самоопределённом языке ассемблера в программу на машинном коде
    
    `converse`(cmd : str, debug_print : bool = False) -> int
        Метод для перевода одной команды в машинный код
    
    `fill_jumps`( : ) -> None
        Метод для заполнения команд прыжков
    
    `make_jump`(type_of_jump : Literal["js", "jns", "je" "jne"]) -> int
        Создание команды на машинном коде для команды прыжка
    
    `split_command`(cmd : str) -> list[str]
        Метод для разбиения исходной команды на список

    `split_attribute`(attr : list) -> (str, int)
        Разбиение операнда на тип и адрес

    `transform_command`(command : list) -> None
        Метод для определения типа команды и обработки (записи параметров) для каждого типа команды

    `set_data`( : ) -> list[str]
        Специальный метод для обработки команды `set`

    `number_10_to_16`(num : int, literal : bool = False) -> int
        Метод для перевода десятичного значения в шестнадцатеричное

    `standart_literal`( : ) -> (int, int)
        Команда для создания переменных команды operand_2 и literal в случае использования literal
    
    `standart_operand`( : ) -> (int, int)
        Команда для создания переменных команды operand_2 и literal в случае использования operand_2
    
    `to_command`( : ) -> int
        Метод для перевода команды в машинный код в зависимости от типа команды

    `print_inner`( : ) -> None:
        Метод для подробного вывода разбиения команды
    
    `clear_inner`( : ) -> None:
        Метод очистки всех внутренних переменных
    """
    def __init__(self):
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

        self.some_massive = []

        self.converse_list = []
        
    def converse_all(self, cmd:list[str], debug_print:bool=False) -> list[int]:
        """Метод для перевода программы на самоопределённом языке ассемблера в программу на машинном коде

        Метод сначала по очереди обрабатывает все команды, запоминая все метки и прыжки, если они есть.
        После первого этапа конверсии проводится вторая, где все команды прыжков дозаполняются по меткам
        
        Parameters
        ----------
        `cmd` : list[str]
            Программа, написанная на самоопределённом языке ассемблера. В каждом элементе списка по одной команде
        
        `debug_print` : bool = False
            Метка, нужно ли подробно расписывать процесс конверсии в консоль
        
        Returns
        -------
        `self.converse_list` : list[int]
            Команда на машинном коде для `ProcessorImitation`
        """
        self.pc = 0
        for command in cmd:
            temp = self.converse(command, debug_print)
            if temp != -2:
                self.converse_list.append(temp)
                self.pc += 1
        
        # Заполнение кодами для команд типа jump с метками
        self.fill_jumps()

        return self.converse_list
    
    def converse(self, cmd:str, debug_print:bool=False) -> int:
        """Метод для перевода одной команды в машинный код
        
        Сначала выполняется лексический анализ, где исходная строка команды разбивается на подстроки.
        Потом производится обработка команды и заполнение внутренних переменных в сооветствии с типом команды. При необходимости печатаются подробности
        Потом команда переводится в машинный код
        После чего внутренние переменные очищаются для подготовки к обработке следующей команды

        Parameters
        ----------
        `cmd` : str
            Одна команда, написанная на самоопределённом языке ассемблера
        
        `debug_print` : bool = False
            Метка, нужно ли подробно расписывать процесс конверсии в консоль
        
        Returns
        -------
        `m_command` : int
            Переведённая команда на машинном коде
        """
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

        # Очистка внутренних переменных для последующих команд
        self.clear_inner()
        return m_command
    
    def fill_jumps(self) -> None:
        """Метод для заполнения команд прыжков
        
        Для повторного прохождения по списку команды. 
        В случае нахождения специальной метки (-1) в команде она конвертируется по сохранённым внутренним параметрам

        Результат записывается во внутреннюю переменную `converse_list`
        """
        for i in range(len(self.converse_list)):
            if self.converse_list[i] == -1:
                type_jump = self.jump_pc[i]
                name_point = self.jump_dict[i]
                number_point = self.point_dict[name_point]
                self.literal = number_point
                self.converse_list[i] = self.make_jump(type_jump)
    
    def make_jump(self, type_of_jump:Literal["js", "jns", "je" "jne"]) -> int:
        """Создание команды на машинном коде для команды прыжка
        
        Используя тип команды, что передаётся в метод, и внутреннюю переменную `literal`, 
        создаётся команда на машинном коде для `ProcessorImitation`

        Parameters
        ----------
        `type_of_jump` : Literal["js", "jns", "je" "jne"]
            Тип прыжка (js, jns, je или jne)
        """
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
        """Метод для разбиения исходной команды на список
        
        Используется регулярное выражение `[ ,:]` для разбиения строки команды

        Parameters
        ----------
        `cmd` : str
            Одна команда, написанная на самоопределённом языке ассемблера
        
        Returns
        -------
        list[int]
            Разбитая команда с помощью паттерна регулярного выражения
        """
        return list(filter(None, re.split(pattern="[ ,:]", string=cmd)))
    
    def split_attribute(self, attr:list) -> (str, int):
        """Разбиение операнда на тип и адрес
        
        Выделяет тип массива и адрес в массиве. 
        Обрабатывает также ссылки (которые обозначены как []) и просто числовые значения для перемещения их в literal

        Parameters
        ----------
        `attr` : list
            Полный операнд из команды
        
        Returns
        -------
        `dest` : str
            Тип массива
        `number` : int
            Адрес в массиве или значение literal
        """
        if attr[0] == "[":
            dest = attr[1]
            number = attr[2:-1]
            self.extra_pin = 2
            return dest, int(number)
        else:
            dest = attr[0]
            number = attr[1:]
            return dest, int(number)
    
    def transform_command(self, command:list) -> None:
        """Метод для определения типа команды и обработки (записи параметров) для каждого типа команды
        
        Команды обрабатываются в том числе в зависимости от количества переменных в ней. В случае несоответствия выкидывается ошибка.
        Результаты обработки записываются во внутренние переменные
        
        Parameters
        ----------
        `command` : list
            Команда на самоопределённом языке ассемблера, разбитая на тип команд и переменные
        
        Raises
        ------
        Не существует команды : `ValueError`
            Вызывается в случае, если команда, написанная в программе, не поддерживается в данном классе (см. поддерживаемые команды)
        
        Не правильная команда, слишком много переменных : `ValueError`
            Вызывается в случае, если переменных  в команде слишком много. 
            Т.к. здесь реализация двухадресных команд, то длина команды может быть от 2 до 4 единиц, разделённых запятой, двуеточием или пробелом
        """
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
                    raise ValueError("Не правильная команда, слишком много переменных. Их может быть от 2 до 4, а у вас = ", len(command))
    
    def set_data(self) -> list[str]:
        """Специальный метод для обработки команды `set`
        
        Метод проходится по написанному в прогремме после команды `set` массиву и создаёт команды на языке ассемблер для его записи в память данных `ProcessorImitation`

        Returns
        -------
        `commands` : list[str]
            Список команд на языке ассемблер для его записи в память данных `ProcessorImitation`
        """
        commands = []
        for i in range(len(self.some_massive)):
            commands.append(f"mov r0, {self.some_massive[i]}")
            commands.append(f"mov d{i}, r0")
        
        commands.append("mov r0, 0")
        return commands
    
    def number_10_to_16(self, num:int, literal:bool=False) -> int:
        """Метод для перевода десятичного значения в шестнадцатеричное
        
        Также осуществляется проверка на размер числа

        Parameters
        ----------
        `num` : int
            Число, которое надо перевести

        `literal` : bool = False
            Флаг для изменения диапазона числа (с [0, 15] до [0, 255]), необходимый для значения literal
        
        Returns
        -------
        int
            Число в шестнадцатеричном формате
        
        Raises
        ------
        Неверный адрес операнда : `ValueError`
            Если число больше 15 или меньше нуля (при `literal` = False)

        Слишком большое или отрицательное число : `ValueError`
            Если число больше 256 или меньше нуля (при `literal` = True)
        """
        if literal:
            if num > 0xFFFF and num < 0:
                raise ValueError("Слишком большое или отрицательное число", num)
            return "{0:04x}".format(num)

        if num > 15 and num < 0:
            raise ValueError("Неверный адрес операнда", num)
        return "{0:01x}".format(num)
    
    def standart_literal(self) -> (int, int):
        """Команда для создания переменных команды operand_2 и literal в случае использования literal
        
        literal назначается числом согласно внутреннему параметру, operand_2 = 0

        Returns
        -------
        `literal` : int
            Значение literal
        
        `op2` : int
            Значение operand_2 (Ноль в данном случае)
        """
        literal_num = self.number_10_to_16(num=self.literal, literal=True)
        literal = int(f"0x0{literal_num}000", base=16)
        op2 = 0x00000000
        return literal, op2
    
    def standart_operand(self) -> (int, int):
        """Команда для создания переменных команды operand_2 и literal в случае использования operand_2
        
        operand_2 назначается числом согласно внутреннему параметру, literal = 0

        Returns
        -------
        `literal` : int
            Значение literal (Ноль в данном случае)
        
        `op2` : int
            Значение operand_2
        """
        literal = 0x00000000
        in_num = self.number_10_to_16(num=self.memory_number_in)
        op2 = int(f"0x000000{in_num}", base=16)
        return literal, op2
    
    def to_command(self) -> int:
        """Метод для перевода команды в машинный код в зависимости от типа команды
        
        Создаёт команду машинного кода из всех внутренних параметров в зависимости от типа команды.
        Также создаёт заглушки для прыжков (-1) и команды `set` (-2)

        Returns
        -------
        `out_command` : int
            Команда машинного кода
        """
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
    
    def print_inner(self) -> None:
        """Метод для подробного вывода разбиения команды
        
        Вызывается в случае, если параметр `debug_print` = True
        """
        print(f"command_type = {self.command_type}")
        print(f"type_of_memory_dest = {self.type_of_memory_dest}")
        print(f"memory_number_dest = {self.memory_number_dest}")
        print(f"type_of_memory_in = {self.type_of_memory_in}")
        print(f"memory_number_in = {self.memory_number_in}")
        print(f"literal = {self.literal}")
        print(f"extra_pin = {self.extra_pin}")
    
    def clear_inner(self) -> None:
        """Метод очистки всех внутренних переменных"""
        self.command_type = None
        self.type_of_memory_dest = None
        self.memory_number_dest = None
        self.type_of_memory_in = None
        self.memory_number_in = None
        self.literal = None
        self.extra_pin = None
        self.some_massive = []