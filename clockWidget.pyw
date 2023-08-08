import tkinter as tk
from tkinter import font
import webbrowser
import sqlite3 as sqlite
from datetime import datetime as date
from os import path


class ClockWidget:
    def __init__(self, parentWindow, ID, clockWidgetHub):
        self.ID = ID
        self.hub = clockWidgetHub
        
        self.parentWindow = parentWindow
        self.parentWindow.title(ID)
        self.parentWindow.resizable(0, 0)  # window is resizeable via changing font size
        
        self.readSettings()
        self.setGeometry()

        self.clockFont = font.Font(
            family='Consolas',
            size=self.settings['FontSize'],
            weight='bold'
        )
        self.clockFontSmall = font.Font(
            family='Consolas',
            size=20,
            weight='bold'
        )

        self.parentWindow.config(
            bg="#202124"
        )

        self.currentTime = tk.StringVar()  # a mutable String to hold currentTime
        self.apm = tk.StringVar()

        self.timeLabel = tk.Label(self.parentWindow,
                            textvariable=self.currentTime,
                            font=self.clockFont,
                            bg='#202124',
                            fg='white'
        )
        self.timeLabel.grid(row=0, column=0)

        self.apmLabel = tk.Label(self.parentWindow,
                       textvariable=self.apm,
                       font=self.clockFontSmall,
                       bg='#202124',
                       fg='white'
        )
        self.apmLabel.grid(row=0, column=1)
        
        self.changeTimeFormat(self.settings['TimeFormat'])
        self.updateCurrentTime()

        # setting up a cascade menu option
        self.timeFormatMenu = tk.Menu(self.parentWindow, tearoff=False)

        self.timeFormatMenu.add_command(
            label="Standard 12-hour",
            command=lambda: self.changeTimeFormat("standard12")
        )

        self.timeFormatMenu.add_command(
            label="Standard 24-hour",
            command=lambda: self.changeTimeFormat("standard24")
        )
        
        # the rightClickMenu as a whole
        self.rightClickMenu = tk.Menu(self.parentWindow, tearoff=False)

        self.rightClickMenu.add_command(
            label="Toggle Bar (ctrl+r)",
            command=lambda: self.toggleORR()
        )

        self.rightClickMenu.add_separator()

        self.rightClickMenu.add_cascade(
            label="Change Time Format", menu=self.timeFormatMenu
        )

        self.rightClickMenu.add_separator()

        self.rightClickMenu.add_command(
            label="Increase Size (ctrl+'+')",
            command=lambda: self.changeFontSize(10)
        )

        self.rightClickMenu.add_command(
            label="Decrease Size (ctrl+'-')",
            command=lambda: self.changeFontSize(-10)
        )

        self.rightClickMenu.add_separator()

        self.rightClickMenu.add_command(
            label="Close Window",
            command=lambda: self.closeWindow()
        )
        
        self.rightClickMenu.add_command(
            label="More Info",
            command=lambda: webbrowser.open_new_tab(
                "https://github.com/danbsolo/ClockWidget")
        )

        self.parentWindow.bind(
            "<Button-3>", lambda event: self.rightClickPopup(event))


        # ctrl+plus/equal and ctrl+minus to increase and decrease fontSize respectively
        self.parentWindow.bind(
            '<Control-plus>', lambda e: self.changeFontSize(1))
        self.parentWindow.bind(
            '<Control-equal>', lambda e: self.changeFontSize(1))
        self.parentWindow.bind(
            '<Control-minus>', lambda e: self.changeFontSize(-1))
        
        self.parentWindow.bind(
            '<Control-r>', lambda e: self.toggleORR())
        
        # Data is saved on FocusOut event, or when closing the window
        self.parentWindow.bind('<FocusOut>', lambda e: [
            self.saveData()
        ])

        # When user clicks "X" close button, do this~
        self.parentWindow.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())

        # Turn on ORR if it was left on from the last session
        if self.ORRStatusBool:
            self.parentWindow.overrideredirect(self.ORRStatusBool)

    # Decides where to open the menu options. In this case, next to the mouse.
    def rightClickPopup(self, event):
        self.rightClickMenu.tk_popup(event.x_root, event.y_root)

    # SQLite doesn't take Boolean values, so working around that requires utilizing 1 and 0.
    def toggleORR(self):
        self.ORRStatusBool = not self.ORRStatusBool
        self.parentWindow.overrideredirect(self.ORRStatusBool)

        if self.ORRStatusBool:
            self.settings['ORRStatus'] = 1
        else:
            self.settings['ORRStatus'] = 0

        self.hub.db.execute("\
                UPDATE CLOCKSETTINGS\
                SET ORRStatus == ?\
                WHERE ID == ?", (
                    self.settings['ORRStatus'],
                    self.ID
                )
            )
        

    def changeFontSize(self, increment):
        try:
            self.hub.db.execute("\
                UPDATE CLOCKSETTINGS\
                SET FontSize == ?\
                WHERE ID == ?", (
                    self.settings['FontSize'] + increment,
                    self.ID
                )
            )
        except sqlite.IntegrityError:
            return

        self.settings['FontSize'] += increment
        self.clockFont.config(size = self.settings['FontSize'])


    def saveData(self):
        self.hub.db.execute("\
            UPDATE CLOCKSETTINGS\
            SET PositionX == ?,\
            PositionY == ?\
            WHERE ID == ?", (
                self.parentWindow.winfo_rootx() +
                self.hub.adjustPositions['AdjustPositionX'],
                \
                self.parentWindow.winfo_rooty() +
                self.hub.adjustPositions['AdjustPositionY'],
                self.ID
            ))
        
        self.hub.connector.commit()
        

    def closeWindow(self):
        self.saveData()
        self.hub.closeApplication()


    def updateCurrentTime(self):
        now = date.now().strftime(self.timeFormat)
        self.currentTime.set(now)

        self.apm.set(date.now().strftime('%p'))

        self.parentWindow.after(1000, self.updateCurrentTime)

    
    def changeTimeFormat(self, timeFormat):
        self.settings['TimeFormat'] = timeFormat

        if timeFormat == 'standard24':
            self.timeFormat = '%H:%M:%S'
            self.apmLabel.grid_forget()
        elif timeFormat == 'standard12':
            self.timeFormat = '%I:%M:%S'
            self.apmLabel.grid(row=0, column=1)

        self.hub.db.execute("\
                UPDATE CLOCKSETTINGS\
                SET TimeFormat == ?\
                WHERE ID == ?", (
                    self.settings['TimeFormat'],
                    self.ID
                )
            )

    def readSettings(self):
        self.hub.db.execute("\
            SELECT *\
            FROM CLOCKSETTINGS\
            WHERE ID == '{}'".format(
                self.ID
            )
        )

        self.settings = dict(self.hub.db.fetchone())

        if self.settings['ORRStatus']:
            self.ORRStatusBool = True
        else:
            self.ORRStatusBool = False


    def setGeometry(self):
       self.parentWindow.geometry(
            "+{}+{}".format(
                self.settings['PositionX'],
                self.settings['PositionY']
            )
       )



class ClockWidgetHub:
    def __init__(self, rootWindow):
        self.rootWindow = rootWindow
        self.rootWindow.title("ClockWidgetHub")
        self.rootWindow.iconify()

        # absolute path of current folder
        self.parentDir = path.dirname(path.abspath(__file__))

        # path of database (whether it exists or not)
        self.databaseDir = self.parentDir + '/clockWidget.db'

        # *row_factory facilitates casting query results as dictionaries
        self.connector = sqlite.connect(self.databaseDir)  # if no db exists, creates one
        self.connector.row_factory = sqlite.Row
        self.db = self.connector.cursor()


        # inquire if CLOCKSETTINGS table exists
        self.db.execute("\
            SELECT * FROM sqlite_master\
            WHERE tbl_name == 'CLOCKSETTINGS'")
        
        if not self.db.fetchone():
            self.createSQLiteTable()
            self.insertDefaultClockWidget('Clock')
            self.connector.commit()
        
        # now that CLOCKSETTINGS is guaranteed to have at least one entry, open it
        self.db.execute("\
            SELECT ID FROM CLOCKSETTINGS\
            ORDER BY ID")
        
        # this code futureproofs the creation of multiple clockWidget windows. For now though, only one is possible
        for clockWidgetRow in self.db.fetchall():
            clockWidgetRow = dict(clockWidgetRow)

            clockWidget = ClockWidget(
                tk.Toplevel(), clockWidgetRow['ID'], self)
        
        # any clockWidget will do
        self.adjustPositionXYvalues(clockWidget)


    def adjustPositionXYvalues(self, clockWidget):
        clockWidget.parentWindow.update()

        self.adjustPositions = {
            'AdjustPositionX': 
            clockWidget.settings['PositionX'] - 
            clockWidget.parentWindow.winfo_rootx(),\
            \
            'AdjustPositionY': clockWidget.settings['PositionY'] - 
            clockWidget.parentWindow.winfo_rooty()
            }


    def closeApplication(self):
        self.db.close()
        self.connector.close()
        self.rootWindow.destroy()
    

    def createSQLiteTable(self):
        self.db.execute("\
            CREATE TABLE CLOCKSETTINGS(\
            ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
            Title TEXT,\
            PositionX INT NOT NULL DEFAULT 500,\
            PositionY INT NOT NULL DEFAULT 500,\
            FontSize INT NOT NULL \
            DEFAULT 55 CHECK(30 <= FontSize AND FontSize <= 200),\
            ORRStatus BOOLEAN NOT NULL \
            DEFAULT 0 CHECK(ORRStatus IN (0, 1)),\
            TimeFormat BOOLEAN NOT NULL \
            DEFAULT 'standard24' CHECK(TimeFormat IN ('standard12', 'standard24'))\
            )")
    
    def insertDefaultClockWidget(self, title):
        self.db.execute(
            "INSERT INTO CLOCKSETTINGS (Title)\
            VALUES (?)", [title]
        )


if __name__ == "__main__":
    root = tk.Tk()

    ClockWidgetHub(root)

    root.mainloop()

