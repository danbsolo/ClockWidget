import tkinter as tk
from datetime import datetime as date
from os import environ

root = tk.Tk()
root.title('Clock')  # default is 'tk', so we're opting out


def update_time():
    x = date.now().strftime('%I:%M:%S %p')
    now.set(x[:-3])
    apm.set(x[-2:])
    root.after(1000, update_time)


def open_settings():
    with open(config_file, 'r') as config:
        root.geometry(config.read().strip())

    with open(imm_config_file, 'r') as immc:
        global settings
        settings = {}

        for row in immc:
            if row[0] not in ['#', '\n']:
                x = row.split()
                settings[x[0][:-1]] = x[1]


def save():
    with open(config_file, 'w') as config:
        config.write(
            '+{}+{}'.format(str(root.winfo_rootx() + int(settings['rootx_adjust'])),
                            str(root.winfo_rooty() + int(settings['rooty_adjust'])))
        )


template = environ['TRACKER_FILES'] + 'clock/{}'
config_file = template.format('configuration.txt')
imm_config_file = template.format('immutable_configuration.txt')

open_settings()

now = tk.StringVar()
apm = tk.StringVar()

time_label = tk.Label(root, textvariable=now,
                      font=('Cambria', 55, 'bold'),
                      pady=0)
time_label.pack()

apm_label = tk.Label(root, textvariable=apm,
                     font=('Consolas', 12, 'bold'),
                     padx=5)
apm_label.pack(side='right')


root.overrideredirect(settings['ORR'])

# root.bind('<KeyRelease>', lambda q: save())


update_time()
root.protocol('WM_DELETE_WINDOW', lambda: [save(), root.destroy()])
root.mainloop()
