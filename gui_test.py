#!/usr/bin/env python3
from tkinter import filedialog
import tkinter 
from tkinter import *

root = tkinter.Tk()

root.geometry('{}x{}'.format(850, 600))

toolbar = Frame(root)

# TextView Code
S = Scrollbar(root)
T = Text(root, height=25, width=100)
S.pack(side=RIGHT, fill=Y)
T.pack()
S.config(command=T.yview)
T.config(yscrollcommand=S.set)

def file_dialog():
	file = filedialog.askopenfile(parent=root,mode='rb',title='Select a File')
	if file != None:
		data = file.read()
		file.close()
		T.insert(END, data)

menu = Menu(root)
root.config(menu=menu)

menu.add_command(label="Open", command=file_dialog)

toolbar.pack(side=TOP, fill=X)

mainloop()