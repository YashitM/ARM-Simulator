#!/usr/bin/env python3
import binascii
import sys

opcodes = {'0000':'AND', '0001': 'EOR', '0010': 'SUB', '0011': 'RSB', '0100': 'ADD', '0101':'ADC', '0110':'SBC', '0111':'RSC', '1000':'TST', '1001':'TEQ', '1010':'CMP', '1011':'CMN', '1100':'ORR', '1101':'MOV', '1110':'BIC', '1111':'MVN'}
registers = {'R0':0, 'R1':0, 'R2':0, 'R3':0, 'R4':0, 'R5':0, 'R6':0, 'R7':0, 'R8':0, 'R9':0, 'R10':0, 'R11':0, 'R12':0, 'R13':0, 'R14':0, 'R15':0}
flags = {'N': 0, 'Z':0, 'C':0, 'V':0}
conditions = {'0000': flags['Z'], '0001': ~flags['Z'], '0010': flags['C'], '0011': ~flags['C'], '0100': flags['N'], '0101' : ~flags['N'], '0110' : flags['V'], '0111' : ~flags['V'], '1000': flags['C'] * ~flags['Z'], '1001' : flags['C'] | flags['Z'], '1010' : ~(flags['N'] ^ flags['V']), '1011' : flags['N'] ^ flags['V'], '1100' : ~flags['Z'] * ~(flags['N'] ^ flags['V']), '1101' : flags['Z'] | (flags['N'] ^ flags['V']), '1110' : 1}
addressInstructionMap = {}
instructions = []

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	
def dataProcess(instruction):
	cond = instruction[:4]
	immediate = instruction[6]
	opcode = instruction[7:11]
	setConditionCode = instruction[11]
	firstOperandRegister = "R" + str(int(instruction[12:16], 2))
	destinationRegister = "R" + str(int(instruction[16:20], 2))
	operandTwo = instruction[20:]
	shift = 0
	rotate = 0
	imm = 0
	secondOperandRegister = 0
	if "0" in immediate:
		shift = operandTwo[:8]
		regOrImm = shift[7]
		shiftType = shift[5:7]
		shiftAmount = 0
		secondOperandRegister = "R" + str(int(operandTwo[8:], 2))
		if "0" in regOrImm:
			shiftAmount = int(shift[:5], 2)
		else:
			shiftAmount = registers["R" + str(int(shift[:4], 2))]
		if "00" in shiftType:
			registers[secondOperandRegister] = registers[secondOperandRegister] << shiftAmount
		elif "01" in shiftType:
			registers[secondOperandRegister] = registers[secondOperandRegister] >> shiftAmount

		else:
			binstring = bin(registers[secondOperandRegister], 2)[2:]
			binstring = "0" * (32 - len(binstring)) + binstring
			binstring = binstring[32 - shiftAmount] + binstring[:32-shiftAmount]
			registers[secondOperandRegister] = int(binstring, 2)
		print ("DECODE: Operation is", opcodes[opcode], ", First Operand is", firstOperandRegister, ", Second Operand is", secondOperandRegister, ", Destination Register is", destinationRegister)
		print ("Read Registers:", firstOperandRegister, "=", registers[firstOperandRegister], ",", secondOperandRegister, "=", registers[secondOperandRegister])
	else:
		rotate = int(operandTwo[:4], 2)
		imm = int(operandTwo[4:], 2)
		print ("DECODE: Operation is", opcodes[opcode], ", First Operand is", firstOperandRegister, ", immediate Second Operand is", imm, ", Destination Register is", destinationRegister)
		print ("Read Registers:", firstOperandRegister, "=", registers[firstOperandRegister])
	return instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm


def loadStore(instruction):
	immediate = instruction[6]
	prePostIndiex = instruction[7]
	upDownBit = instruction[8]
	byteWordBit = instruction[9]
	writeBackBit = instruction[10]
	loadStoreBit = instruction[11]
	baseRegister = instruction[12:16]
	destinationRegister = instruction[16:20]
	immediateOffset = 0
	shift = 0
	offsetRegister = 0
	if "0" in immediate:
		immediateOffset = instruction[20:]
	else:
		shift = instruction[20:28]
		regOrImm = shift[7]
		shiftType = shift[5:7]
		shiftAmount = 0
		offsetRegister = instruction[28:]
		if "0" in regOrImm:
			shiftAmount = int(shift[:5], 2)
		else:
			shiftAmount = registers["R" + str(int(shift[:4], 2))]
		if "00" in shiftType:
			registers[offsetRegister] = registers[offsetRegister] << shiftAmount
		elif "01" in shiftType:
			registers[offsetRegister] = registers[offsetRegister] >> shiftAmount
		else:
			binstring = bin(registers[offsetRegister], 2)[2:]
			binstring = "0" * (32 - len(binstring)) + binstring
			binstring = binstring[32 - shiftAmount] + binstring[:32-shiftAmount]
			registers[offsetRegister] = int(binstring, 2)
		
def branchInstructions(instruction):
	if conditions[instruction[:4]]:	
		if "10" in instruction[4:6]:
			if "1" in instruction[6]:
				registers['R14'] = registers['R15'] + 4
			offset = int(instruction[8:], 2)
			return offset
		else:
			bRegisterValue = registers["R" + str(int(instruction[28:], 2))]
			registers['R15'] = bRegisterValue
			return 0

	else:
		print ("EXECUTE:", "no execution as condition not satisfied for branch statement")
		return 4
	

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def executeData(instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm):
	def mov(register, value):
		registers[register] = value

	def add(destination, valueOne, valueTwo):
		registers[destination] = valueOne + valueTwo

	def sub(destination, valueOne, valueTwo):
		registers[destination] = valueOne - valueTwo

	def rsb(destination, valueOne, valueTwo):
		registers[destination] = valueTwo - valueOne

	def eor(destination, valueOne, valueTwo):
		registers[destination] = valueOne ^ valueTwo

	def orr(destination, valueOne, valueTwo):
		registers[destination] = valueOne | valueTwo

	def AND(destination, valueOne, valueTwo):
		registers[destination] = valueOne & valueTwo

	def bic(destination, valueOne, valueTwo):
		registers[destination] = valueOne & ~valueTwo

	def mvn(destination, value):
		registers[destination] = ~value

	def cmp(valueOne, valueTwo):
		value = valueOne - valueTwo
		if value < 0:
			flags['N'] = 1
			flags['V'] = 0
		else:
			flags['N'] = 0
		if value == 0:
			flags['Z'] = 1
		else:
			flags['Z'] = 0
		if value > 0:
			flags['V'] = 0


	if "MOV" in opcodes[opcode]:
		if "0" in immediate:
			mov(destinationRegister, registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[secondOperandRegister], "in", destinationRegister)
		else:
			mov(destinationRegister, imm)
			print ("EXECUTE:", opcodes[opcode], imm, "in", destinationRegister)

	if "ADD" in opcodes[opcode]:
		if "0" in immediate:
			add(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			add(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])	

	if "SUB" in opcodes[opcode]:
		if "0" in immediate:
			sub(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			sub(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])

	if "RSB" in opcodes[opcode]:
		if "0" in immediate:
			rsb(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			rsb(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])

	if "EOR" in opcodes[opcode]:
		if "0" in immediate:
			eor(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			eor(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])

	if "ORR" in opcodes[opcode]:
		if "0" in immediate:
			orr(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			orr(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])

	if "BIC" in opcodes[opcode]:
		if "0" in immediate:
			bic(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			bic(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])

	if "AND" in opcodes[opcode]:
		if "0" in immediate:
			AND(destinationRegister, registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			AND(destinationRegister, registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])

	if "CMP" in opcodes[opcode]:
		f "0" in immediate:
			cmp(registers[firstOperandRegister], registers[secondOperandRegister])
			print ("EXECUTE:", opcodes[opcode], registers[firstOperandRegister], "and", registers[secondOperandRegister])		
		else:
			cmp(registers[firstOperandRegister], imm)
			print ("EXECUTE:", opcodes[opcode], imm, "and", registers[destinationRegister])




#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
	with open('input.MEM', 'r') as f:
		instructions = f.readlines()
	for i in range(len(instructions)):
		instructions[i] = instructions[i].rstrip("\n")
		add, inst = instructions[i].split(" ")
		addressInstructionMap[int(add, 16)] = inst
		if i == 0:
			registers['R15'] = int(add, 16)
	print (addressInstructionMap)
	while True:
		offset = 4
		i = addressInstructionMap[registers['R15']]
		print ("Fetch instruction", i, "from address", hex(registers['R15']))
		if "0xEF000011" in i:
			print ("No memory operation")
			print ("EXIT:")
			sys.exit()
		i = "0" * (32 - len(bin(int(i, 16))[2:])) + bin(int(i, 16))[2:]

		print (i)
		if "00" in i[4:6] and "111111111111" not in i[12:24]:
			instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm = dataProcess(i)
			executeData(instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm)	
		elif "01" in i[4:6]:
			loadStore(i)
		elif "10" in i[4:6] or ("00" in i[4:6] and "111111111111" in instruction[12:24]):
			offset = branchInstructions(i)
		print ("MEMORY: No memory operation")
		print ("WRITEBACK: write", registers[destinationRegister], "to", destinationRegister)
		print ()
		registers['R15'] += offset
	print (registers)


#1110 00 1 1101 0 0000 0010 000000001010