import tkinter as tk
from random import randint

#ебу собак всегда готов
#трахать сразу несколько котов
win = tk.Tk()
win.title("bablo")
win.geometry("500x500")
res = tk.Label(win, text = "-")
res.grid(row = 3, column = 0)
bablo = 0
def onclick():
    global bablo
    bablo += 100000
    res.configure(text = "баланс = " + str(bablo) + "$")
bb1 = tk.Button(win, text = "кнопка бабло", command = onclick)
bb1.grid(row = 1, column = 1)
# да, я зоофил, не говори
#лучше мне собачку подари!


win.mainloop()