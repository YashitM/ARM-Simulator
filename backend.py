#!/usr/bin/env python3
import binascii
import sys

opcodes = {'0000':'AND', '0001': 'EOR', '0010': 'SUB', '0011': 'RSB', '0100': 'ADD', '0101':'ADC', '0110':'SBC', '0111':'RSC', '1000':'TST', '1001':'TEQ', '1010':'CMP', '1011':'CMN', '1100':'ORR', '1101':'MOV', '1110':'BIC', '1111':'MVN'}
registers = {'R0':0, 'R1':0, 'R2':0, 'R3':0, 'R4':0, 'R5':0, 'R6':0, 'R7':0, 'R8':0, 'R9':0, 'R10':0, 'R11':0, 'R12':0, 'R13':0, 'R14':0, 'R15':0}
instructions = []

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def decode(i):
	address, instruction = i.split(" ")
	print ("Fetch instruction", instruction, "from address", address)
	if "0xEF000011" in instruction:
		print ("No memory operation")
		print ("EXIT:")
		sys.exit()
	instruction = bin(int(instruction.strip("0x"), 16))[2:]
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
		regOrImm = shift[8]
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
		elif "10" in shiftType:

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
	return address, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def execute(address, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm):
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

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

with open('input.MEM', 'r') as f:
	instructions = f.readlines()
for i in range(len(instructions)):
	instructions[i] = instructions[i].rstrip("\n")
i = 0
while i < len(instructions):

	address, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm = decode(instructions[i])
	execute(address, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm)	
	
	print ("MEMORY: No memory operation")
	print ("WRITEBACK: write", registers[destinationRegister], "to", destinationRegister)
	print ()
	i += 1
print (registers)


#1110 00 1 1101 0 0000 0010 000000001010