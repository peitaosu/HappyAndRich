import os, sys, json, datetime

class Happy():
    def __init__(self, name, onboard_date, conversion_date, leave_date="2099-01-01"):
        self.name = name
        self.onboard_date = datetime.datetime.strptime(onboard_date, "%Y-%m-%d")
        self.conversion_date = datetime.datetime.strptime(conversion_date, "%Y-%m-%d")
        self.leave_date = datetime.datetime.strptime(leave_date, "%Y-%m-%d")

    def update_attendation(self, year, month):
        self.attendation = Attendation(self.name, year, month)
        self.attendation.init_attendation("{}-{}.json".format(year, month))
        self.attendation.update_attendation()
        self.attendation.update_late()

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
        self.update()

    def update(self):
        self.base = int(input("Input base: "))
        if self.happy.onboard_date.month == int(self.month) or self.happy.conversion_date.month == int(self.month) or self.happy.leave_date.month == int(self.month):
            self.month_day = self.happy.attendation.month_day
        if (self.happy.conversion_date.year == int(self.year) and self.happy.conversion_date.month < int(self.month)) or (self.happy.conversion_date.year < int(self.year)):
            self.probation = False
        else:
            self.probation = True
            self.probation_percent = float(input("Input probation percent: "))
        self.food_bonus = list(self.happy.attendation.workdays.values()).count(1) * self.food_bonus_per_day
        if len(self.happy.attendation.sick_leave) + len(self.happy.attendation.personal_leave) > 0:
            self.attend_bonus = 0
        if sum(self.happy.attendation.late.values()) > 3:
            self.attend_bonus = sum(self.happy.late.values()) * self.attend_bonus_per_day
        self.phone_bonus = int(input("Input phone bonus: "))
        self.other_bonus = int(input("Input other bonus: "))
        if len(self.happy.attendation.sick_leave) > 0:
            current_date = datetime.datetime.strptime("{}-{}-{}".format(self.year, self.month, self.happy.onboard_date.day), "%Y-%m-%d")
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
            for work_date in self.happy.attendation.workdays.keys():
                if int(work_date) < self.happy.conversion_date.day:
                    before_convert += self.happy.attendation.workdays[work_date] * (1.0 - self.probation_percent)
            for holiday_date in self.happy.attendation.holidays.keys():
                if int(holiday_date) < self.happy.conversion_date.day:
                    before_convert += self.happy.attendation.holidays[holiday_date] * (1.0 - self.probation_percent)
            leave_before_convert = 0
            leave_after_convert = 0
            for sick_date in self.happy.attendation.sick_leave.keys():
                if int(sick_date) < self.happy.conversion_date.day:
                    leave_before_convert += self.happy.attendation.sick_leave[sick_date] * (1.0 - self.sick_leave_percent * self.probation_percent) + (1 - self.happy.attendation.sick_leave[sick_date]) * (1 - self.probation_percent) 
                else:
                    leave_after_convert += self.happy.attendation.sick_leave[sick_date] * (1.0 - self.sick_leave_percent)
            for personal_date in self.happy.attendation.personal_leave.keys():
                if int(personal_date) < self.happy.conversion_date.day:
                    leave_before_convert += self.happy.attendation.personal_leave[personal_date]
                else:
                    leave_after_convert += self.happy.attendation.personal_leave[personal_date]
            self.salary -= self.base / self.month_day * before_convert + self.base / self.month_day * leave_before_convert + self.base / self.month_day * leave_after_convert
            over_before_convert = 0
            over_after_convert = 0
            for over_date in self.happy.attendation.overtime.keys():
                if int(over_date) < self.happy.conversion_date.day:
                    over_before_convert += self.happy.attendation.overtime[over_date] * self.probation_percent
                else:
                    over_after_convert += self.happy.attendation.overtime[over_date]
            self.salary += self.base / self.month_day * (over_before_convert + over_after_convert)
        elif self.happy.conversion_date.year == int(self.year) and self.happy.conversion_date.month > int(self.month) or self.happy.conversion_date.year > int(self.year):
            self.salary = self.base * self.probation_percent
            self.salary -= self.base / self.month_day * (sum(self.happy.attendation.sick_leave.values()) * (1.0 - self.sick_leave_percent) + sum(self.happy.attendation.personal_leave.values()))
            self.salary += self.base / self.month_day * sum(self.happy.attendation.overtime.values()) * self.probation_percent
        else:
            self.salary = self.base
            self.salary -= self.base / self.month_day * (sum(self.happy.attendation.sick_leave.values()) * (1.0 - self.sick_leave_percent) + sum(self.happy.attendation.personal_leave.values()))
            self.salary += self.base / self.month_day * sum(self.happy.attendation.overtime.values())
        self.salary += self.food_bonus + self.attend_bonus + self.phone_bonus + self.other_bonus
        print(self.salary)
                

class Attendation():
    def __init__(self, name, year, month):
        self.name = name
        self.year = year
        self.month = month
        self.month_day = 0
        
        self.workdays = {}
        self.holidays = {}
        self.weekends = {}
        self.overtime = {}
        self.annual_leave = {}
        self.sick_leave = {}
        self.personal_leave = {}
        self.funeral_leave = {}
        self.marriage_leave = {}
        self.maternity_leave = {}

        self.late = {}

    def init_attendation(self, calendar_file):
        with open(calendar_file) as in_file:
            calendar = json.load(in_file)
        for date in calendar[self.year][self.month].keys():
            if calendar[self.year][self.month][date]["workday"]:
                self.month_day += 1
                self.workdays[date] = 1
                continue
            if calendar[self.year][self.month][date]["holiday"]:
                self.month_day += 1
                self.holidays[date] = 1
                continue
            if calendar[self.year][self.month][date]["weekend"]:
                self.weekends[date] = 1
                continue
    
    def _handle_input(self, input_str):
        output = {}
        if input_str == "0": return {}
        for date_str in input_str.split(","):
            date = date_str
            count = 1
            if ":" in date_str:
                date = date_str.split(":")[0]
                count = float(date_str.split(":")[1])
            output[date] = count
        return output

    def update_attendation(self):
        overtimes = self._handle_input(input("Input overtimes: "))
        for overtime in overtimes:
            self.overtime[overtime] = overtimes[overtime]
            if overtimes[overtime] == 1:
                self.overtime[overtime] = 0
            else:
                self.overtime[overtime] = self.overtime[overtime] - overtimes[overtime]
        annual_leaves = self._handle_input(input("Input annual leaves: "))
        for annual in annual_leaves:
            self.annual_leave[annual] = annual_leaves[annual]
            if annual_leaves[annual] == 1:
                self.workdays[annual] = 0
            else:
                self.workdays[annual] = self.workdays[annual] - annual_leaves[annual]
        sick_leaves = self._handle_input(input("Input sick leaves: "))
        for sick in sick_leaves:
            self.sick_leave[sick] = sick_leaves[sick]
            if sick_leaves[sick] == 1:
                self.workdays[sick] = 0
            else:
                self.workdays[sick] = self.workdays[sick] - sick_leaves[sick]
        personal_leaves = self._handle_input(input("Input personal leaves: "))
        for personal in personal_leaves:
            self.personal_leave[personal] = personal_leaves[personal]
            if personal_leaves[personal] == 1:
                self.workdays[personal] = 0
            else:
                self.workdays[personal] = self.workdays[personal] - personal_leaves[personal]
        funeral_leaves = self._handle_input(input("Input funeral leaves: "))
        for funeral in funeral_leaves:
            self.funeral_leave[funeral] = funeral_leaves[funeral]
            if funeral_leaves[funeral] == 1:
                self.workdays[funeral] = 0
            else:
                self.workdays[funeral] = self.workdays[funeral] - funeral_leaves[funeral]
        marriage_leaves = self._handle_input(input("Input marriage leaves: "))
        for marriage in marriage_leaves:
            self.marriage_leave[marriage] = marriage_leaves[marriage]
            if marriage_leaves[marriage] == 1:
                self.workdays[marriage] = 0
            else:
                self.workdays[marriage] = self.workdays[marriage] - marriage_leaves[marriage]
        maternity_leaves = self._handle_input(input("Input maternity leaves: "))
        for maternity in maternity_leaves:
            self.maternity_leave[maternity] = maternity_leaves[maternity]
            if maternity_leaves[maternity] == 1:
                self.workdays[maternity] = 0
            else:
                self.workdays[maternity] = self.workdays[maternity] - maternity_leaves[maternity]

    def update_late(self):
        self.lates = self._handle_input(input("Input lates: "))

happy = Happy("陈紫菁", "2020-10-10", "2021-01-10")
happy.update_attendation("2021", "02")
rich = Rich(happy, "2021", "02")
rich.get_salary()

