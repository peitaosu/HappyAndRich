import os, sys, json, calendar, datetime
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

class CAL_UI(QMainWindow):
    def __init__(self, current_year, current_month):
        super(CAL_UI, self).__init__()
        uic.loadUi("cal.ui", self)
        self.Calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.Calendar.setCurrentPage(int(current_year), int(current_month))
        self.Calendar.clicked[QDate].connect(self.update_type)
        self.DateType.currentTextChanged.connect(self.type_updated)
        self.ResetButton.clicked.connect(self.reset_all)
        self.SaveButton.clicked.connect(self.save_all)
        self.current_year = current_year
        self.current_month = current_month
        self.my_calendar = { self.current_year: { self.current_month: {}}}
        self.month_range = calendar.monthrange(int(self.current_year), int(self.current_month))
        self.workday_color = QTextCharFormat()
        self.workday_color.setForeground(Qt.blue)
        self.weekend_color = QTextCharFormat()
        self.weekend_color.setForeground(Qt.gray)
        self.holiday_color = QTextCharFormat()
        self.holiday_color.setForeground(Qt.cyan)
        self.reset_all()
    
    def reset_all(self):
        self.my_calendar = { self.current_year: { self.current_month: {}}}
        for date in list(range(1, self.month_range[1] + 1)):
            if datetime.datetime.strptime("{}-{}-{}".format(self.current_year, self.current_month, date), "%Y-%m-%d").isoweekday() > 5:
                self.my_calendar[self.current_year][self.current_month][str(date)] = {
                    "workday": False,
                    "holiday": False,
                    "weekend": True
                }
                self.Calendar.setDateTextFormat(QDate(int(self.current_year), int(self.current_month), date), self.weekend_color)
            else:
                self.my_calendar[self.current_year][self.current_month][str(date)] = {
                    "workday": True,
                    "holiday": False,
                    "weekend": False
                }
                self.Calendar.setDateTextFormat(QDate(int(self.current_year), int(self.current_month), date), self.workday_color)

    def update_type(self, date):
        if self.my_calendar[self.current_year][self.current_month][str(date.day())]["workday"]:
            self.DateType.setCurrentText("Workday")
        elif self.my_calendar[self.current_year][self.current_month][str(date.day())]["weekend"]:
            self.DateType.setCurrentText("Weekend")
        elif self.my_calendar[self.current_year][self.current_month][str(date.day())]["holiday"]:
            self.DateType.setCurrentText("Holiday")

    def type_updated(self, value):
        if value == "Workday":
            self.my_calendar[self.current_year][self.current_month][str(self.Calendar.selectedDate().day())] = {
                "weekend": False,
                "workday": True,
                "holiday": False
            }
            self.Calendar.setDateTextFormat(self.Calendar.selectedDate(), self.workday_color)
        elif value == "Weekend":
            self.my_calendar[self.current_year][self.current_month][str(self.Calendar.selectedDate().day())] = {
                "weekend": True,
                "workday": False,
                "holiday": False
            }
            self.Calendar.setDateTextFormat(self.Calendar.selectedDate(), self.weekend_color)
        elif value == "Holiday":
            self.my_calendar[self.current_year][self.current_month][str(self.Calendar.selectedDate().day())] = {
                "weekend": False,
                "workday": False,
                "holiday": True
            }
            self.Calendar.setDateTextFormat(self.Calendar.selectedDate(), self.holiday_color)

    def save_all(self):
        with open("{}-{}.json".format(self.current_year, self.current_month), "w") as out_file:
            json.dump(self.my_calendar, out_file, indent=4)
        self.close()
        

if __name__ == '__main__':
    cal = QApplication(sys.argv)
    cal_ui = CAL_UI(sys.argv[1], sys.argv[2])
    cal_ui.show()
    cal.exec_()
