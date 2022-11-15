#Python script that uses tkinter to show the position of the CNC machine in real time.
#Tkinter window is a black background with a white circle that repersents the CNC Machine position
#Tkinter window size  is 600*(180*2) pixels
#The CNC machine is 180mm deep and 300mm wide
#The CNC machine is moving at 3000mm/min
import tkinter as tk
import time

#Frequently Used Variables
FSPEED = 3000
x = 5
y = 5
x_length = 600
y_length = 360

#Setup tkinter
root = tk.Tk()
root.title("CNC Machine Position")
root.geometry("600x360")
root.configure(background='black')
canvas = tk.Canvas(root, width=x_length, height=y_length, bg="black")
CNC = canvas.create_oval(x, y, x+10, y+10, fill="white")


#Add a ruler to the top of the tkinter windows from 0 to 300mm
for i in range(0, 600, 50):
    canvas.create_line(i, 5, i, 1, fill="white")
    canvas.create_text(i, 7, text=str(i), fill="white")

#Add a ruler to the left side of the tkinter window from 0 to 180mm
for i in range(0, 360, 50):
    canvas.create_line(7, i, 1, i, fill="white")
    canvas.create_text(9, i, text=str(i), fill="white")

#Move the CNC oval to a new position ( 100 , 100)
def moveCNC(x, y):
    canvas.move(CNC, x, y)
    root.update()

canvas.pack()
moveCNC(150, 150)
canvas.pack()
root.mainloop()
