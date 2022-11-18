#Python script that uses tkinter to show the position of the CNC machine in real time.
#Tkinter window is a black background with a white circle that repersents the CNC Machine position
#Tkinter window size  is 600*(180*2) pixels
#The CNC machine is 180mm deep and 300mm wide
#The CNC machine is moving at 3000mm/min
import tkinter as tk
import time

#Frequently Used Variables
FSPEED = 4500
CNC_x = 5
CNC_y = 5
x_length = 600 #(300 * 2)
y_length = 360 #(180 * 2)

#Create a Tkinter windows using the x_length and y_length variables as the size of the window with a black background and a white circle that represents the CNC machine
root = tk.Tk()
root.title("CNC Machine Position")
root.geometry(f'{x_length}x{y_length}')
root.configure(bg='black')
canvas = tk.Canvas(root, width=x_length, height=y_length, bg='black')
canvas.pack()
canvas.create_oval(CNC_x, CNC_y, 20, 20, fill='white')
#Add a listener for when i click the escape key to close the Tkinter window
root.bind('<Escape>', lambda e: root.destroy())

#Add a ruler to the top of the Tkinter window from 0 to 300mm with a 25mm interval
for i in range(0, 301, 25):
    canvas.create_line(i*2, 0, i*2, 10, fill='white')
    canvas.create_text(i*2, 15, text=i, fill='white', font=('Arial', 8))
#Add a ruler to the left side of the Tkinter window from 0 to 180mm with a 25mm interval
for i in range(0, 181, 25):
    canvas.create_line(0, i*2, 10, i*2, fill='white')
    canvas.create_text(15, i*2, text=i, fill='white', font=('Arial', 8))

#Create a function that moves the CNC machine oval to a specific location over a period of time (time is calculated using the distance between the current location and the new location and the speed of the CNC machine)
def move(x, y):
    global CNC_x
    global CNC_y
    global canvas
    global root
    global FSPEED
    
    currentPosition = {
        'x': CNC_x,
        'y': CNC_y
    }
    
    #Calculate the distance between the current location and the new location
    distance = ((x-CNC_x)**2 + (y-CNC_y)**2)**0.5
    #Calculate the time it will take to move from the current location to the new location
    time_to_move = distance / (FSPEED/60)
    #Calculate the number of steps it will take to move from the current location to the new location
    steps = int(time_to_move * 100)
    #Calculate the distance between each step
    x_step = (x-CNC_x)/steps
    y_step = (y-CNC_y)/steps
    #Move the CNC machine oval to the new location over a period of time
    for i in range(steps):
        CNC_x += x_step
        CNC_y += y_step
        canvas.coords(1, CNC_x, CNC_y, CNC_x+15, CNC_y+15)
        root.update()
        time.sleep(0.01)




move(600, 0)


#Make the Tkinter window stay open
root.mainloop()

