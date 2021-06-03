import os, sys, json

year = input("Input year: ")
month = input("Input month: ")
workdays = str(input("Input workdays: ")).split(",")
holidays = str(input("Input holidays: ")).split(",")
weekends = str(input("Input weekends: ")).split(",")

calendar = {year: {month: {}}}
for workday in workdays:
    if workday in calendar[year][month]:
        print("ERROR: {} already in calendar.".format(workday))
    calendar[year][month][workday] = {
        "workday": True,
        "holiday": False,
        "weekend": False
    }
for holiday in holidays:
    if holiday in calendar[year][month]:
        print("ERROR: {} already in calendar.".format(holiday))
    calendar[year][month][holiday] = {
        "workday": False,
        "holiday": True,
        "weekend": False
    }
for weekend in weekends:
    if weekend in calendar[year][month]:
        print("ERROR: {} already in calendar.".format(weekend))
    calendar[year][month][weekend] = {
        "workday": False,
        "holiday": False,
        "weekend": True
    }

with open("{}-{}.json".format(year, month), "w") as out_file:
    json.dump(calendar, out_file, indent=4)