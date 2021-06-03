import os, sys, json, calendar, datetime
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

class Happy():
    def __init__(self, name, onboard_date, conversion_date, leave_date="2099-01-01"):
        self.name = name
        self.onboard_date = onboard_date
        self.conversion_date = conversion_date
        self.leave_date = leave_date

    def update_attendation(self, attendation, month_day, late):
        self.attendation = attendation
        self.attendation_lates = late
        self.attendation_month_day = month_day

class Rich():
    def __init__(self, happy, year, month):
        self.happy = happy
        self.year = year
        self.month = month
        self.base = 0
        self.salary = 0
        self.food_bonus = 0
        self.food_bonus_per_day = 25
        self.attend_bonus = 200
        self.attend_bonus_per_day = -50
        self.phone_bonus = 0
        self.other_bonus = 0
        self.month_day = 21.75
        self.sick_leave_percent = 0.6

    def update(self, base, probation_percent, phone_bonus, other_bonus):
        self.base = base
        self.probation_percent = probation_percent
        if self.happy.onboard_date.month == int(self.month) or self.happy.conversion_date.month == int(self.month) or self.happy.leave_date.month == int(self.month):
            self.month_day = self.happy.attendation_month_day
        if (self.happy.conversion_date.year == int(self.year) and self.happy.conversion_date.month < int(self.month)) or (self.happy.conversion_date.year < int(self.year)):
            self.probation = False
        else:
            self.probation = True
        if (self.happy.leave_date.year == int(self.year) and self.happy.leave_date.month == int(self.month)):
            self.leave = self.happy.leave_date.day
        else:
            self.leave = False
        if (self.happy.onboard_date.year == int(self.year) and self.happy.onboard_date.month == int(self.month)):
            self.onboard = self.happy.onboard_date.day
        else:
            self.onboard = False
        # TO FIX
        if self.onboard:
            food_bonus_count = 0
            for workday in self.happy.attendation["Workday"].keys():
                if int(workday) >= self.happy.onboard_date.day and self.happy.attendation["Workday"][workday] == 1:
                    food_bonus_count += 1
            self.food_bonus = food_bonus_count * self.food_bonus_per_day
        elif self.leave:
            food_bonus_count = 0
            for workday in self.happy.attendation["Workday"].keys():
                if int(workday) <= self.happy.leave_date.day and self.happy.attendation["Workday"][workday] == 1:
                    food_bonus_count += 1
            self.food_bonus = food_bonus_count * self.food_bonus_per_day
        else:
            self.food_bonus = list(self.happy.attendation["Workday"].values()).count(1) * self.food_bonus_per_day
        if (len(self.happy.attendation["Sick Leave"]) + len(self.happy.attendation["Personal Leave"]) + self.happy.attendation_lates > 0) or self.probation or self.leave:
            self.attend_bonus = 0
        if self.happy.attendation_lates > 3:
            self.attend_bonus = self.happy.attendation_lates * self.attend_bonus_per_day
        self.phone_bonus = phone_bonus
        self.other_bonus = other_bonus
        if len(self.happy.attendation["Sick Leave"]) > 0:
            current_date = datetime.datetime.strptime("{}-{}-{}".format(self.year, self.month, self.happy.onboard_date.day), "%Y-%m-%d").date()
            if current_date < self.happy.onboard_date.replace(year = self.happy.onboard_date.year + 2):
                self.sick_leave_percent = 0.6
            elif current_date < self.happy.onboard_date.replace(year = self.happy.onboard_date.year + 4):
                self.sick_leave_percent = 0.7
            elif current_date < self.happy.onboard_date.replace(year = self.happy.onboard_date.year + 6):
                self.sick_leave_percent = 0.8
            elif current_date < self.happy.onboard_date.replace(year = self.happy.onboard_date.year + 8):
                self.sick_leave_percent = 0.9
            else:
                self.sick_leave_percent = 1.0

    def get_salary(self):
        if self.happy.conversion_date.year == int(self.year) and self.happy.conversion_date.month == int(self.month):
            self.salary = self.base
            before_convert = 0.0
            for work_date in self.happy.attendation["Workday"].keys():
                if int(work_date) < self.happy.conversion_date.day:
                    before_convert += self.happy.attendation["Workday"][work_date] * (1.0 - self.probation_percent)
            for holiday_date in self.happy.attendation["Holiday"].keys():
                if int(holiday_date) < self.happy.conversion_date.day:
                    before_convert += self.happy.attendation["Holiday"][holiday_date] * (1.0 - self.probation_percent)
            leave_before_convert = 0
            leave_after_convert = 0
            for sick_date in self.happy.attendation["Sick Leave"].keys():
                if int(sick_date) < self.happy.conversion_date.day:
                    leave_before_convert += self.happy.attendation["Sick Leave"][sick_date] * (1.0 - self.sick_leave_percent * self.probation_percent) + (1 - self.happy.attendation["Sick Leave"][sick_date]) * (1 - self.probation_percent) 
                else:
                    leave_after_convert += self.happy.attendation["Sick Leave"][sick_date] * (1.0 - self.sick_leave_percent)
            for personal_date in self.happy.attendation["Personal Leave"].keys():
                if int(personal_date) < self.happy.conversion_date.day:
                    leave_before_convert += self.happy.attendation["Personal Leave"][personal_date]
                else:
                    leave_after_convert += self.happy.attendation["Personal Leave"][personal_date]
            self.salary -= self.base / self.month_day * before_convert + self.base / self.month_day * leave_before_convert + self.base / self.month_day * leave_after_convert
            over_before_convert = 0
            over_after_convert = 0
            for over_date in self.happy.attendation["Overtime"].keys():
                if int(over_date) < self.happy.conversion_date.day:
                    over_before_convert += self.happy.attendation["Overtime"][over_date] * self.probation_percent
                else:
                    over_after_convert += self.happy.attendation["Overtime"][over_date]
            self.salary += self.base / self.month_day * (over_before_convert + over_after_convert)
        elif self.happy.conversion_date.year == int(self.year) and self.happy.conversion_date.month > int(self.month) or self.happy.conversion_date.year > int(self.year):
            self.salary = self.base * self.probation_percent
            if self.onboard:
                self.salary -= self.base * self.probation_percent / self.month_day * (len([1 for day in self.happy.attendation["Workday"].keys() if int(day) < self.onboard]) + len([1 for day in self.happy.attendation["Holiday"].keys() if int(day) < self.onboard]))
            self.salary -= self.base / self.month_day * (sum(self.happy.attendation["Sick Leave"].values()) * (1.0 - self.sick_leave_percent) + sum(self.happy.attendation["Personal Leave"].values()))
            self.salary += self.base / self.month_day * sum(self.happy.attendation["Overtime"].values()) * self.probation_percent
        elif self.happy.leave_date.year == int(self.year) and self.happy.leave_date.month == int(self.month):
            self.salary = self.base
            self.salary -= self.base / self.month_day * len([1 for day in self.happy.attendation["Workday"].keys() if int(day) > self.leave]) 
            self.salary -= self.base / self.month_day * (sum(self.happy.attendation["Sick Leave"].values()) * (1.0 - self.sick_leave_percent) + sum(self.happy.attendation["Personal Leave"].values()))
            self.salary += self.base / self.month_day * sum(self.happy.attendation["Overtime"].values()) * self.probation_percent
        else:
            self.salary = self.base
            self.salary -= self.base / self.month_day * (sum(self.happy.attendation["Sick Leave"].values()) * (1.0 - self.sick_leave_percent) + sum(self.happy.attendation["Personal Leave"].values()))
            self.salary += self.base / self.month_day * sum(self.happy.attendation["Overtime"].values())
        self.salary += self.food_bonus + self.attend_bonus + self.phone_bonus + self.other_bonus
        return {
            "Base": self.base,
            "Probation %": self.probation_percent,
            "Food Bonus": self.food_bonus,
            "Attendation Bonus": self.attend_bonus,
            "Phone Bonus": self.phone_bonus,
            "Other Bonus": self.other_bonus,
            "Total": self.salary
        }

class HR_UI(QMainWindow):
    def __init__(self, current_year, current_month):
        super(HR_UI, self).__init__()
        uic.loadUi("hr.ui", self)
        self.AttendationCalendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.AttendationCalendar.setCurrentPage(int(current_year), int(current_month))
        self.ResetButton.clicked.connect(self.reset_attendation)
        self.CalculateButton.clicked.connect(self.calculate)
        

        self.AttendationCalendar.clicked[QDate].connect(self.update_type_day)
        self.DateType.currentTextChanged.connect(self.type_updated)
        self.Days.currentTextChanged.connect(self.day_updated)

        self.current_year = current_year
        self.current_month = current_month
        self.attendation = { self.current_year: { self.current_month: {}}}
        self.month_range = calendar.monthrange(int(self.current_year), int(self.current_month))
        self.workday_color = QTextCharFormat()
        self.workday_color.setForeground(Qt.blue)
        self.weekend_color = QTextCharFormat()
        self.weekend_color.setForeground(Qt.gray)
        self.holiday_color = QTextCharFormat()
        self.holiday_color.setForeground(Qt.cyan)
        self.sick_color = QTextCharFormat()
        self.sick_color.setForeground(Qt.darkRed)
        self.personal_color = QTextCharFormat()
        self.personal_color.setForeground(Qt.red)
        self.annual_color = QTextCharFormat()
        self.annual_color.setForeground(Qt.darkCyan)
        self.marriage_color = QTextCharFormat()
        self.marriage_color.setForeground(Qt.magenta)
        self.maternity_color = QTextCharFormat()
        self.maternity_color.setForeground(Qt.darkMagenta)
        self.funeral_color = QTextCharFormat()
        self.funeral_color.setForeground(Qt.darkGray)
        self.overtime = QTextCharFormat()
        self.overtime.setForeground(Qt.darkBlue)
        self.reset_attendation()

    def reset_attendation(self):
        with open("{}-{}.json".format(self.current_year, self.current_month)) as in_file:
            self.default_calendar = json.load(in_file)
        self.month_day = 0
        for date in self.default_calendar[self.current_year][self.current_month].keys():
            if self.default_calendar[self.current_year][self.current_month][date]["workday"] or self.default_calendar[self.current_year][self.current_month][date]["holiday"]:
                self.month_day += 1
        self.attendation = {
            "Workday" : {},
            "Holiday" : {},
            "Weekend" : {},
            "Overtime" : {},
            "Annual Leave" : {},
            "Sick Leave" : {},
            "Personal Leave" : {},
            "Funeral Leave" : {},
            "Marriage Leave" : {},
            "Maternity Leave" : {}
        }
        self.onboard_date = self.OnboardDate.date().toPyDate()
        self.conversion_date = self.ConversionDate.date().toPyDate()
        self.leave_date = self.LeaveDate.date().toPyDate()
        for date in self.default_calendar[self.current_year][self.current_month]:
            if self.default_calendar[self.current_year][self.current_month][date]["workday"]:
                """
                if self.onboard_date.year == int(self.current_year) and self.onboard_date.month == int(self.current_month) and self.onboard_date.day > int(date):
                    continue
                if self.leave_date.year == int(self.current_year) and self.leave_date.month == int(self.current_month) and self.leave_date.day < int(date):
                    continue
                """
                self.attendation["Workday"][date] = 1
                self.AttendationCalendar.setDateTextFormat(QDate(int(self.current_year), int(self.current_month), int(date)), self.workday_color)
            elif self.default_calendar[self.current_year][self.current_month][date]["holiday"]: 
                self.attendation["Holiday"][date] = 1
                self.AttendationCalendar.setDateTextFormat(QDate(int(self.current_year), int(self.current_month), int(date)), self.holiday_color)
            elif self.default_calendar[self.current_year][self.current_month][date]["weekend"]: 
                self.attendation["Weekend"][date] = 1
                self.AttendationCalendar.setDateTextFormat(QDate(int(self.current_year), int(self.current_month), int(date)), self.weekend_color)

    def calculate(self):
        self.happy = Happy(self.NameEdit.text(), self.OnboardDate.date().toPyDate(), self.ConversionDate.date().toPyDate(), self.LeaveDate.date().toPyDate())
        self.happy.update_attendation(self.attendation, self.month_day, int(self.LateEdit.text()))
        self.rich = Rich(self.happy, self.current_year, self.current_month)
        self.rich.update(int(self.BaseEdit.text()), float(self.ProbationEdit.text()) if self.ProbationEdit.text() else 1, int(self.PhoneEdit.text()), int(self.OtherEdit.text()))
        salary = self.rich.get_salary()
        self.SummaryTable.setRowCount(len(salary))
        self.SummaryTable.setColumnCount(2)
        row = 0
        for item in salary:
            self.SummaryTable.setItem(row, 0, QTableWidgetItem(item))
            self.SummaryTable.setItem(row, 1, QTableWidgetItem(str(salary[item])))
            row += 1
    
    def update_type_day(self, date):
        day = str(date.day())
        for date_type in self.attendation:
            if day in self.attendation[date_type]:
                if date_type == "Workday" and self.attendation[date_type][day] != 1: continue
                self.DateType.setCurrentText(date_type)
                self.Days.setCurrentText(str(self.attendation[date_type][day]))

    def type_updated(self, type):
        current_day = self.Days.currentText()
        current_date = str(self.AttendationCalendar.selectedDate().day())
        if current_day == "0.5":
            current_day = float(current_day)
        else:
            current_day = int(current_day)
        for date_type in self.attendation:
            if date_type == type:
                self.attendation[date_type][current_date] = current_day
            else:
                if current_date in self.attendation[date_type]:
                    if current_day == 1:
                        self.attendation[date_type].pop(current_date, None)
                    else:
                        self.attendation[date_type][current_date] =  1 - current_day

    def day_updated(self, day):
        pass
        current_date = str(self.AttendationCalendar.selectedDate().day())
        if day == "0.5":
            day = float(day)
        else:
            day = int(day)
        self.attendation[str(self.DateType.currentText())][current_date] = day

if __name__ == '__main__':
    hr = QApplication(sys.argv)
    hr_ui = HR_UI(sys.argv[1], sys.argv[2])
    hr_ui.show()
    hr.exec_()
