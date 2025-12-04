import serial
import time
import csv
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import math
import random

class RCIApp:
    def __init__(self, master):
        self.master = master
        master.title("IRS Monitor")
        self.use_dummy = True
        self.data_frame = pd.DataFrame(columns=['Time', 'Temperature', 'Pressure', 'Mass Flow'])
        self.fig, self.ax = plt.subplots()
        self.line1, = self.ax.plot([], [], label = 'Temperature')
        self.line2, = self.ax.plot([], [], label = 'Pressure')
        self.line3, = self.ax.plot([], [], label = 'Mass Flow')
        self.ax.legend()
        self.ax.set_xlabel("Time(ms)")
        self.ax.set_ylabel("Values(SI Units)")

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.start_button = tk.Button(master, text = "START", command = self.start_read)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.stop_button = tk.Button(master, text = "STOP", command = self.stop_read)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.live_label = tk.Label(master, text = "Temperature : -- Pressure : -- Mass Flow : --", font=("Arial", 12))
        self.live_label.pack(side=tk.LEFT, padx=10)
        self.is_reading = False
        self.serial_thread = None

    def start_read(self):
        if not self.is_reading:
            print("Starting to read data")
            self.is_reading = True
            self.serial_thread = threading.Thread(target=self.read_and_update)
            self.serial_thread.daemon = True
            self.serial_thread.start()
            self.update_plot()
        
    def stop_read(self):
        self.is_reading = False

    def read_and_update(self):
        ser_port = serial.Serial(port = 'COM3', baudrate=115200, timeout=1)
        print(f"Starting to read data from {ser_port.port} at the rate of {ser_port.baudrate}bps")
        if not self.use_dummy:
            try:
                ser_port = serial.Serial(port='COM3', baudrate=115200, timeout=1)
                print(f"Can access {ser_port.port}")
            except:
                print("Serial connection failed")
        start_time = time.time()
        while self.is_reading:
            if self.use_dummy:
                elapsed = (time.time() - start_time) * 1000
                temp = 25 + random.uniform(-0.5, 5) + 0.3 * math.sin(time.time())
                press = 1010 + random.uniform(-3, 3)
                mf = abs(1.5 + random.uniform(-1, 1) * math.sin(time.time()*2))
                row = {'Time' : elapsed, 'temp' : temp, 'press' : press, 'mf' : mf}
                self.data_frame = pd.concat([self.data_frame, pd.DataFrame([row])], ignore_index=True)
            else:
                if ser_port.in_waiting > 0:
                    line = ser_port.readline().decode('utf-8').strip()
                    if line:
                        t, temp, press, mf = line.split(",")
                        row = {'Time' : float(t), 'temp' : float(temp), 'press' : float(press), 'mf' : float(mf)}
                        self.data_frame = pd.concat([self.data_frame, pd.DataFrame([row])], ignore_index=True)
            self.master.after(0, lambda t=temp, p=press, m=mf : self.live_label.config(text=f"Temperature : {t:.2f}K Pressure : {p:.2f}bar Mass Flow : {m:.2f}nlpm"))
            time.sleep(0.1)
        
    def update_plot(self):
        if not self.data_frame.empty:
            self.line1.set_data(self.data_frame['Time'], self.data_frame['temp'])
            self.line2.set_data(self.data_frame['Time'], self.data_frame['press'])
            self.line3.set_data(self.data_frame['Time'], self.data_frame['mf'])
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        if self.is_reading:
            self.master.after(1000, self.update_plot)

root = tk.Tk()
app = RCIApp(root)
root.mainloop()