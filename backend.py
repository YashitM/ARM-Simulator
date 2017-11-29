#!/usr/bin/env python3
import binascii
import sys
from bitstring import Bits

opcodes = {'0000':'AND', '0001': 'EOR', '0010': 'SUB', '0011': 'RSB', '0100': 'ADD', '0101':'ADC', '0110':'SBC', '0111':'RSC', '1000':'TST', '1001':'TEQ', '1010':'CMP', '1011':'CMN', '1100':'ORR', '1101':'MOV', '1110':'BIC', '1111':'MVN'}
registers = {'R0':0, 'R1':0, 'R2':0, 'R3':0, 'R4':0, 'R5':0, 'R6':0, 'R7':0, 'R8':0, 'R9':0, 'R10':0, 'R11':0, 'R12':0, 'R13':0, 'R14':0, 'R15':0}
flags = {'N': 0, 'Z':0, 'C':0, 'V':0}
conditions = {'0000': "flags['Z']", '0001': "negate(flags['Z'])", '0010': "flags['C']", '0011': "negate(flags['C'])", '0100': "flags['N']", '0101' : "negate(flags['N'])", '0110' : "flags['V']", '0111' : "negate(flags['V'])", '1000': "flags['C'] * negate(flags['Z'])", '1001' : "flags['C'] | flags['Z']", '1010' : "(negate(flags['N']) | flags['Z'])", '1011' : "flags['N'] ^ flags['V']", '1100' : "negate(flags['Z']) * negate((flags['N']) ^ flags['V'])", '1101' : "flags['Z'] | (flags['N'] ^ flags['V'])", '1110' : '1'}
addressInstructionMap = {}
memoryBuffer = {}
literalPool = {200: None, 204:None, 208:None, 212:None}
instructions = []
heapAllocated = []

S = ""



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def negate(a):
	
	if a == 0:
		return 1
	else:
		return 0
	
def dataProcess(instruction):
	#1110 00 0 1010 1 0000 0000 000000000001
	global S
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
	totalShift = 0
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
			totalShift = registers[secondOperandRegister] << shiftAmount
		elif "01" in shiftType:
			totalShift = registers[secondOperandRegister] >> shiftAmount

		else:
			binstring = bin(registers[secondOperandRegister], 2)[2:]
			binstring = "0" * (32 - len(binstring)) + binstring
			binstring = binstring[32 - shiftAmount] + binstring[:32 - shiftAmount]
			totalShift = int(binstring, 2)
		S += "DECODE: Operation is " + opcodes[opcode] + ", First Operand is " + firstOperandRegister + ", Second Operand is " + secondOperandRegister + ", Destination Register is " + destinationRegister + "\n"
		S += "Read Registers: "+ firstOperandRegister + " = " + str(registers[firstOperandRegister]) + ", " + secondOperandRegister + " = " + str(registers[secondOperandRegister]) + "\n"
	else:
		rotate = int(operandTwo[:4], 2)
		imm = int(operandTwo[4:], 2)
		S += "DECODE: Operation is " + opcodes[opcode] + ", First Operand is " + firstOperandRegister + ", immediate Second Operand is " + str(imm) + ", Destination Register is " + destinationRegister + "\n"
		S += "Read Registers: " + firstOperandRegister + " = " + str(registers[firstOperandRegister]) + "\n"
	return totalShift, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm


def loadStore(instruction):
	#1110 01 0 1 1 0 0 0 0110 0101 000000000100
	#1110 01 0 1 1 1 0 1 0001 0000 000000000000
	global S
	immediate = instruction[6]
	prePostIndiex = instruction[7]
	upDownBit = instruction[8]
	byteWordBit = instruction[9]
	writeBackBit = instruction[10]
	loadStoreBit = instruction[11]
	baseRegister = "R" + str(int(instruction[12:16], 2))
	destinationRegister = "R" + str(int(instruction[16:20], 2))
	immediateOffset = 0
	shift = 0
	offsetRegister = 0
	totalShift = 0
	if "R15" in baseRegister:
		registers[destinationRegister] = literalPool[registers['R15'] + int(instruction[20:], 2)]
	else:
		if "0" in immediate:
			immediateOffset = int(instruction[20:], 2)
			totalShift = immediateOffset
		else:
			shift = instruction[20:28]
			regOrImm = shift[7]
			shiftType = shift[5:7]
			shiftAmount = 0
			offsetRegister = "R" + str(int(instruction[28:], 2))
			if "0" in regOrImm:
				shiftAmount = int(shift[:5], 2)
			else:
				shiftAmount = registers["R" + str(int(shift[:4], 2))]
			if "00" in shiftType:
				totalShift = registers[offsetRegister] << shiftAmount
			elif "01" in shiftType:
				totalShift = registers[offsetRegister] >> shiftAmount
			else:
				binstring = bin(registers[offsetRegister], 2)[2:]
				binstring = "0" * (32 - len(binstring)) + binstring
				binstring = binstring[32 - shiftAmount] + binstring[:32 - shiftAmount]
				totalshift = int(binstring, 2)

		if "0" in upDownBit:
			totalShift *= -1
		if "1" in loadStoreBit:
			#L.append(memoryBuffer,  totalShift)
			S += "DECODE: Operation is LDR, Base register is " + baseRegister + ", Destination register is " + destinationRegister + ", offset is " + str(totalShift)
			
			if "1" in prePostIndiex:
				if type(memoryBuffer[registers[baseRegister]]) == list:
					if "0" in byteWordBit:
						registers[destinationRegister] = memoryBuffer[registers[baseRegister]][totalShift // 4]
					else:
						registers[destinationRegister] = ord(memoryBuffer[registers[baseRegister]][totalShift])
				else:
					registers[destinationRegister] = memoryBuffer[registers[baseRegister] + totalShift]
				S += ", pre index increment enabled \n"
				"""
				if "1" in writeBackBit:
					L.append(", write back enabled")
					register[baseRegister] += totalshift
				else:
					L.append(", write back disabled")
				"""
				S += "Read registers: " + baseRegister + " = " + str(registers[baseRegister]) + "\n"
				S += "MEMORY: value from address " + hex(registers[baseRegister] + totalShift) + " read \n"
			"""
			else:
				registers[destinationRegister] = memoryBuffer[registers[baseRegister]]
				register[baseRegister] += totalshift
				print(", post index increment enabled")
				L.append("MEMORY: value from address", hex(registers[baseRegister]), "read")
			"""
			S += "WRITEBACK: write " + str(registers[destinationRegister]) + " to " + destinationRegister + "\n\n"
		else:
			S += "DECODE: Operation is STR, Base register is " + baseRegister + ", Source register is " + destinationRegister + ", offset is " + str(totalShift) 
			
			if "1" in prePostIndiex:
				S += ", pre index increment enabled\n"
				if totalShift % 4 != 0:
					S += "memory alignment error\n"
					sys.exit()
				else:
					if type(memoryBuffer[registers[baseRegister]]) == list:
						if "0" in byteWordBit:
							memoryBuffer[registers[baseRegister]][totalShift // 4] = registers[destinationRegister]
						else:
							memoryBuffer[registers[baseRegister]][totalShift] = registers[destinationRegister]
					else:
						memoryBuffer[registers[baseRegister] + totalShift] = registers[destinationRegister]
				"""
				if "1" in writeBackBit:
					L.append(", write back enabled")
					if type(memoryBuffer[registers[baseRegister]]) == list:
						registers[baseRegister] += (totalShift // 4) * 32
					else:
						registers[baseRegister] += totalshift
				else:
					L.append(", write back disabled")
				"""
				S += "Read registers: " + destinationRegister + " = " + str(registers[destinationRegister]) + "\n"
				S += "MEMORY: " + str(registers[destinationRegister]) + " written to " + hex(registers[baseRegister] + totalShift) + "\n"
			"""
			else:
				if type(memoryBuffer[registers[baseRegister]]) == list:
						memoryBuffer[registers[baseRegister]][0] = registers[destinationRegister]
					else:
						memoryBuffer[registers[baseRegister] + totalShift] = registers[destinationRegister]
				memoryBuffer[registers[baseRegister]][0] = registers[destinationRegister]
				registers[baseRegister] += totalshift
				print(", post index increment enabled")
				L.append("MEMORY:", registers[destinationRegister], "written to", hex(registers[baseRegister]))
			"""
			S += "WRITEBACK: No writeback \n\n"

def branchInstructions(instruction):
	#print(instruction[:4])#, conditions[instruction[:4]])
	#L.append(flags)
	global S
	if eval(conditions[instruction[:4]]):	
		#L.append("Condition Satisfied")

		if "10" in instruction[4:6]:

			binstring = instruction[8:] + "00"
			if "0" in binstring[0]:
				binstring = "000000" + binstring
			else:
				binstring = "111111" + binstring
			a = Bits(bin = binstring)
			offset = a.int

			if "1" in instruction[6]:
				S += "DECODE: Branch and Link " + " to offset " + hex(offset + 8) +"\n"
				registers['R14'] = registers['R15'] + 4
			else:
				S += "DECODE: Branch to offset " + hex(offset + 8) + "\n"
			S += "Read registers: No registers read\n" 
			S += "EXECUTE: branching to " + hex(offset + 8) + "\n"
			return offset + 8

		else:
			bRegisterValue = registers["R" + str(int(instruction[28:], 2))]
			registers['R15'] = bRegisterValue
			return 0

	else:
		S += "EXECUTE: " + "no execution as condition not satisfied for branch statement \n"
		return 4
	

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def executeData(totalShift, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm):
	global S
	def mov(register, value):
		registers[register] = value

	def add(destination, valueOne, valueTwo):
		#L.append("Register values", valueOne, valueTwo)
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
		registers[destination] = valueOne & ~(valueTwo)

	def mvn(destination, value):
		registers[destination] = ~(value)

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
			mov(destinationRegister, totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[secondOperandRegister]) + " in " + destinationRegister + "\n"
		else:
			mov(destinationRegister, imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " in " + destinationRegister + "\n"

	if "ADD" in opcodes[opcode]:
		if "0" in immediate:
			add(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			add(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"	

	if "SUB" in opcodes[opcode]:
		if "0" in immediate:
			sub(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			sub(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "RSB" in opcodes[opcode]:
		if "0" in immediate:
			rsb(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			rsb(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "EOR" in opcodes[opcode]:
		if "0" in immediate:
			eor(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			eor(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "ORR" in opcodes[opcode]:
		if "0" in immediate:
			orr(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			orr(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "BIC" in opcodes[opcode]:
		if "0" in immediate:
			bic(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			bic(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "AND" in opcodes[opcode]:
		if "0" in immediate:
			AND(destinationRegister, registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			AND(destinationRegister, registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "CMP" in opcodes[opcode]:
		if "0" in immediate:
			cmp(registers[firstOperandRegister], totalShift)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(registers[firstOperandRegister]) + " and " + str(registers[secondOperandRegister]) + "\n"		
		else:
			cmp(registers[firstOperandRegister], imm)
			S += "EXECUTE: " + opcodes[opcode] + " " + str(imm) + " and " + str(registers[destinationRegister]) + "\n"

	if "MVN" in opcodes[opcode]:

		mvn(destinationRegister, totalShift)
		S += "EXECUTE: " + opcodes[opcode] + "\n"		





#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def main(fileName):
	global S
	with open(fileName, 'r') as f:
		instructions = f.readlines()
	for i in range(len(instructions)):
		instructions[i] = instructions[i].rstrip("\n")
		add, inst = instructions[i].split(" ")
		addressInstructionMap[int(add, 16)] = inst
		if i == 0:
			registers['R15'] = int(add, 16)
	#L.append(addressInstructionMap)

	toReturn = ""


	while True:
		
		offset = 4
		i = addressInstructionMap[registers['R15']]
		#L.append(i)
		S = ""
		S += "Fetch instruction " + i + " from address " + hex(registers['R15']) + "\n"
		if "0xEF000011".lower() in i.lower():
			S += "DECODE: SWI_EXIT \n"
			S += "No memory operation \n"
			S += "EXIT:"
			#L.append(registers)
			#L.append(memoryBuffer)
			return (toReturn, registers, flags)
			sys.exit()

		if "0xEF000000".lower() in i.lower():
			S += "DECODE: SWI print character \n"
			S += "Read registers R0 = " + chr(registers['R0']) + "\n"
			S += "EXECUTE: " + chr(registers['R0']) + "\n"
			print (chr(registers['R0']))

		if "0xEF000002".lower() in i.lower():
			
			string = ""
			for r in memoryBuffer[registers['R0']]:
				string += r
			L.append(string)

		if "0xEF000012".lower() in i.lower():
			S += "DECODE: SWI Mem Alloc \n"
			S += "Read registers: " + 'R0 is ' + str(registers['R0']) + "\n"
			S += "EXECUTE: No execute operation \n"
			size = registers['R0']
			L = [None] * size
			memoryBuffer[id(L[0])] = L
			registers['R0'] = id(L[0])
			S += "MEMORY: Space allocated in memory at location " + hex(id(L[0])) + "\n"
			S += "WRITEBACK: " + hex(id(L[0])) + " to R0 \n"
			heapAllocated.append(id(L[0]))

		if "0xEFOOOO13".lower() in i.lower():
			for r in heapAllocated:
				del memoryBuffer[r]
			S += "DECODE: SWI Deallocate all heap allocated memory \n"
			S += "Read registers: no registers read\n"
			S += "EXECUTE: no execute operation\n"
			S += "MEMORY: Deleted memory block\n"
			S += "WRITEBACK: No writeback\n"

		if "0xEF000069".lower() in i.lower():
			S += "DECODE: SWI print String\n"
			S += "Read Registers: " + "R0 = " + str(registers['R0']) + ", R1 = " + hex(registers['R1']) + "\n"
			S += "EXECUTE: No execute operation\n"
			S += "MEMORY: String loaded from " + hex(registers['R1']) + "\n"
			S += "WRITEBACK: no writeback\n"
			if registers['R0'] == 1:
				string = ""
				for r in memoryBuffer[registers['R1']]:
					string += r
				L.append(string)

		if "0xEF00006C".lower() in i.lower():
			S += "DECODE: SWI interger input\n"
			S += "Read registers: R0 = " + str(registers['R0']) + "\n"
			S += "EXECUTE: no execute operation\n"
			S += "MEMORY: No memory operation\n"

			if registers['R0'] == 0:
				registers['R0'] = int(input("Give integer input: "))
			S += "WRITEBACK: " + str(registers['R0']) + " written to R0\n"

		if "0xEF00006A".lower() in i.lower():
			S += "DECODE: SWI string input\n"
			S += "Read registers: R0 = " + str(registers['R0']) + " R1 = " + hex(registers['R1']) + " R2 = " + str(registers['R2']) + "\n"
			S += "EXECUTE: no execute operation\n"
			S += "MEMORY: writes string at base address " + hex(registers['R1']) + "\n"
			S += "WRITEBACK: " + str(registers['R2']) + " written to R0\n"
			if registers['R0'] == 0:
				string = input("Give string input: ")
				if len(string) > registers['R2']:
					string = string[:registers['R2']]
				for c in range(len(string)):
					memoryBuffer[registers['R1']][c] = string[c]
				registers['R0'] = registers['R2']

		if "0xEF00006B".lower() in i.lower():
			S += "DECODE: SWI integer output"
			S += "Read registers: R0 = " + str(registers['R0']) + " R1 = " + str(registers['R1']) + "\n"
			S += "EXECUTE: Prints from R1\n"
			S += "MEMORY: No memory operation\n"
			S += "WRITEBACK: No Writeback\n"
			if registers['R0'] == 1:
				print (registers['R1'])
			else:
				S += "Invalid file descriptor\n"
				sys.exit()
		i = "0" * (32 - len(bin(int(i, 16))[2:])) + bin(int(i, 16))[2:]

		#L.append(i)
		if "00" in i[4:6] and "111111111111" not in i[12:24]:
			totalShift, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm = dataProcess(i)
			executeData(totalShift, instruction, cond, opcode, immediate, setConditionCode, firstOperandRegister, destinationRegister, shift, operandTwo, secondOperandRegister, rotate, imm)	
			S += "MEMORY: No memory operation\n"
			if "CMP" not in opcodes[opcode]:
				S += "WRITEBACK: write " + str(registers[destinationRegister]) + " to " + destinationRegister + "\n\n"
			else:
				S += "WRITEBACK: no writeback\n\n"
		elif "01" in i[4:6]:
			loadStore(i)
		elif "10" in i[4:6] or ("00" in i[4:6] and "111111111111" in instruction[12:24]):
			offset = branchInstructions(i)
			S += "MEMORY: No memory operation\n"
			S += "WRITEBACK: No writeback operation \n\n"
	
		registers['R15'] += offset

		# print (S)
		toReturn += S
	


#1110 00 1 1101 0 0000 0010 000000001010

#1110 1010 111111111111111111111001
if __name__ == '__main__':
	main('input3.MEM')