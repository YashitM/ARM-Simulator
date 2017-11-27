#!/usr/bin/env python3
import binascii
opcodes = {'0000':'AND', '0001': 'EOR', '0010': 'SUB', '0011': 'RSB', '0100': 'ADD', '0101':'ADC', '0110':'SBC', '0111':'RSC', '1000':'TST', '1001':'TEQ', '1010':'CMP', '1011':'CMN', '1100':'ORR', '1101':'MOV', '1110':'BIC', '1111':'MVN'}
registers = {'R0':0, 'R1':0, 'R2':0, 'R3':0, 'R4':0, 'R5':0, 'R6':0, 'R7':0, 'R8':0, 'R9':0, 'R10':0, 'R11':0, 'R12':0, 'R13':0, 'R14':0, 'R15':0}

instructions = []
with open('input.MEM', 'r') as f:
	instructions = f.readlines()
for i in range(len(instructions)):
	instructions[i] = instructions[i].rstrip("\n")
for i in instructions:
	address, instruction = i.split(" ")
	print ("Fetch instruction", instruction, "from address", address)
	instruction = bin(int(instruction.strip("0x"), 16))[2:]
	cond = instruction[:4]
	immediate = instruction[6]
	opcode = instruction[7:11]
	setConditionCode = instruction[11]
	firstOperandRegister = "R" + str(int(instruction[12:16], 2))
	destinationRegister = "R" + str(int(instruction[16:20], 2))
	operandTwo = instruction[20:]
	shift = 0
	secondOperandRegister = 0
	rotate = 0
	imm = 0
	if "0" in immediate:
		shift = operandTwo[:8]
		secondOperandRegister = operandTwo[8:]
	else:
		rotate = int(operandTwo[:4], 2)
		imm = int(operandTwo[4:], 2)
	print ("DECODE: Operation is", opcodes[opcode], ", First Operand is", firstOperandRegister, ", immediate Second Operand is", imm, ", Destination Register is", destinationRegister)
	print ("Read Registers:", firstOperandRegister, "=", registers[firstOperandRegister])
	print ("EXECUTE:", opcodes[opcode], imm, "in", destinationRegister)
	print ("MEMORY: No memory operation")
	print ()
#1110 00 1 1101 0 0000 0010 000000001010