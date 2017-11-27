#!/usr/bin/env python3
from tkinter import filedialog
import tkinter 
from tkinter import *
# import backend
import time

registers = {'R0':0, 'R1':0, 'R2':0, 'R3':0, 'R4':0, 'R5':0, 'R6':0, 'R7':0, 'R8':0, 'R9':0, 'R10':0, 'R11':0, 'R12':0, 'R13':0, 'R14':0, 'R15':0}
flags = {'N': 0, 'Z':0, 'C':0, 'V':0}

root = tkinter.Tk()

root.geometry('{}x{}'.format(850, 600))

toolbar = Frame(root)

# Global padding values
xAxis = 2
yAxis = 2


# TextView Main Text Code
S1 = Scrollbar(root)
T1 = Text(root, height=20, width=80)
S1.grid(row = 1, column = 1, rowspan=2,  sticky=N+S+W)
T1.grid(row = 1, column = 0)
S1.config(command=T1.yview)
T1.config(yscrollcommand=S1.set)

# TextView Registers Code
S2 = Scrollbar(root)
T2 = Text(root, height=20, width=20)
S2.grid(row = 1, column = 3, rowspan=2,  sticky=N+S+W)
T2.grid(row = 1, column = 2)
S2.config(command=T2.yview)
T2.config(yscrollcommand=S2.set)

# Button Code
def executeButton():
	print ("Working")
	lineNumber = 1
	for line in T1.get('1.0', 'end-1c').splitlines():
		if line:
			print('path: {}'.format(line))
		lineNumber += 1
B = tkinter.Button(root, text ="Execute", padx=xAxis, pady=yAxis, command=executeButton)
B.grid(row = 2, column = 0)

#TextView2 Code
S3 = Scrollbar(root)
T3 = Text(root, height=10, width=80)
S3.grid(row = 3, column = 1, rowspan = 2, sticky=N+S+W)
T3.grid(row = 3, column = 0)
S3.config(command=T3.yview)
T3.config(yscrollcommand=S3.set)

def file_dialog():
	file = filedialog.askopenfile(parent=root,mode='rb',title='Select a File')
	if file != None:
		data = file.read()
		file.close()
		T1.insert(END, data)

def showRegisters():
	for i in registers:
		T2.insert(END, i+":\t"+str(registers[i])+"\n")
	for i in flags:
		T2.insert(END, i+":\t"+str(flags[i])+"\n")


menu = Menu(root)
root.config(menu=menu)
menu.add_command(label="Open", command=file_dialog)
toolbar.grid(row = 0)
showRegisters()
mainloop()