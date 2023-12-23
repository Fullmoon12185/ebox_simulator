
# import csv
 
# filename ="boxes.csv"
 
# # opening the file using "with"
# # statement
# arraybox = []
# with open(filename, 'r') as data:
#   for line in csv.DictReader(data):
#       arraybox.append(line)
      
# for box in arraybox:
#     print(box["BoxID"])
#     print(box["BoxName"])

# import pygsheets
# import pandas as pd
# #authorization
# gc = pygsheets.authorize(service_file='./creds1.json')

# # Create empty dataframe
# df = pd.DataFrame()

# # Create a column
# df['name'] = ['John', 'Steve', 'Sarah']

# #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
# sh = gc.open('Ebox Data Gathering')

# #select the first sheet 
# wks = sh[0]

# #update the first sheet with df, starting at cell B2. 
# wks.set_dataframe(df,(1,1))


# from oauth2client.service_account import ServiceAccountCredentials
# import gspread
# import json

# scopes = [
# 'https://www.googleapis.com/auth/spreadsheets',
# 'https://www.googleapis.com/auth/drive'
# ]

# credentials = ServiceAccountCredentials.from_json_keyfile_name("./creds1.json", scopes) #access the json key you downloaded earlier 
# file = gspread.authorize(credentials) # authenticate the JSON key with gspread
# sheet = file.open('Ebox Data Gathering') #open sheet
# sheet = sheet.sheet1 #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1

# sheet.update_acell('C2', 'Blue')

# sheet.update_cell(2, 3, 'Blue') #updates row 2 on column 3

# sheet.update('A2:B3', [["Not Ford", "Not Lancia"], ["Nothing", "Not"]])

print("hello world")
