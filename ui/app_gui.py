
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import BOTH
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.database import get_recent_glucose

# Kreiranje glavnog prozora
app = ttk.Window(themename="darkly")
app.title("Glukoza - poslednja 3 dana")
app.geometry("1000x800")

# Prikaz grafa u okviru
frame = ttk.Frame(app)
frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

# Povlačenje podataka
data = get_recent_glucose(days=1)

if data:
    timestamps, values = [], []
    for t, v in data:
        try:
            timestamps.append(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ"))
        except:
            try:
                timestamps.append(datetime.strptime(t, "%Y-%m-%d %H:%M"))
            except:
                timestamps.append(datetime.strptime(t, "%Y-%m-%d %H:%M:%S"))
        values.append(v)

    # Kreiranje matplotlib grafa
    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    ax.plot(timestamps, values, marker='o', linestyle='-', label="Glukoza (mmol/L)")
    ax.set_title(" Vrednosti glukoze (3 dana)")
    ax.set_ylabel("mmol/L")
    ax.set_xlabel("Vreme")
    ax.grid(True)
    fig.autofmt_xdate()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    plt.close(fig)
else:
    ttk.Label(frame, text="⚠️ Nema dostupnih podataka.", bootstyle="warning").pack(pady=20)

# Pokreni prozor
app.mainloop()
