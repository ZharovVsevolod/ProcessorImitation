from utils.assembler import AssemblerConversion
from utils.processor import ProcessorImitation

with open("programs/find_max_in_data.txt") as prog:
    cmd = [line.rstrip() for line in prog]
print(cmd)

assembler_unit = AssemblerConversion()
commands = assembler_unit.converse_all(cmd)
for comd in commands:
    print("{0:08x}".format(comd))

process = ProcessorImitation(register_size=4, data_memory=16, command_memory=commands)
process.command_loop()