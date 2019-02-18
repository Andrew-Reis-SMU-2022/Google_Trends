import pandas as pd
import datetime
import os
import requests
import xlsxwriter
import matplotlib.pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')


for file in os.listdir('simfin_data'):
    raw_df = pd.read_excel(f'simfin_data/{file}')
    new_df = {}
    new_df[raw_df.columns[0]] = []
    for i in range(1, len(raw_df.columns)):
        new_df[raw_df.columns[0]].append(raw_df.columns[i])
    for i in range(len(raw_df.index)):
        new_df[raw_df.iloc[i, 0]] = []
        for j in range(1, len(raw_df.columns)):
            new_df[raw_df.iloc[i, 0]].append(raw_df.iloc[i, j])

df_simfin = pd.DataFrame(new_df)
dates = []
quarter_key = df_simfin.columns[0]
revenue_key = df_simfin.columns[1]
for quarter in df_simfin[quarter_key]:
    year_str = '20' + quarter.split(" '")[1]
    quarter_str = quarter.split(" '")[0]
    if quarter_str == 'Q1':
        quarter_date = datetime.date(int(year_str), 3, 31)
    elif quarter_str == 'Q2':
        quarter_date = datetime.date(int(year_str), 6, 30)
    elif quarter_str == 'Q3':
        quarter_date = datetime.date(int(year_str), 9, 30)
    elif quarter_str == 'Q4':
        quarter_date = datetime.date(int(year_str), 12, 31)
    dates.append(quarter_date)
df_simfin['Date'] = dates
df_simfin['Date'] = pd.to_datetime(df_simfin['Date'])
df_simfin = df_simfin.set_index('Date')

revenue_percent_change = []
for revenue in df_simfin[revenue_key]:
    revenue_percent_change.append((float(revenue) - float(df_simfin[revenue_key][0])) / float(df_simfin[revenue_key][0]))

df_simfin['Revenue_Percent_Change'] = revenue_percent_change
df_simfin['Revenue_Percent_Change'].plot()

class Quarter:
    def __init__(self, year, quarter_str):
        self.year = year
        self.quarter_str = quarter_str
        if quarter_str == 'Q1':
            self.month_nums = {1, 2, 3}
        elif quarter_str == 'Q2':
            self.month_nums = {4, 5, 6}
        elif quarter_str == 'Q3':
            self.month_nums = {7, 8, 9}
        elif quarter_str == 'Q4':
            self.month_nums = {10, 11, 12}

        if quarter_str == 'Q1':
            self.quarter_date = datetime.date(year, 3, 31)
        elif quarter_str == 'Q2':
            self.quarter_date = datetime.date(year, 6, 30)
        elif quarter_str == 'Q3':
            self.quarter_date = datetime.date(year, 9, 30)
        elif quarter_str == 'Q4':
            self.quarter_date = datetime.date(year, 12, 31)

        self.activity_values = []

    def calc_total_activity(self):
        self.total_activity = sum(self.activity_values)

for file in os.listdir('trend_data'):
    df_trend = pd.read_csv(f'trend_data/{file}')
    activity_key = df_trend.columns[1]
    quarter_list = []
    for quarter in df_simfin[quarter_key]:
        quarter_list.append(Quarter(2000 + int(quarter.split(" '")[1]), quarter.split(" '")[0]))
    for i in range(len(df_trend.index)):
        for quarter in quarter_list:
            if int(df_trend['Month'][i].split('-')[0]) == quarter.year and int(df_trend['Month'][i].split('-')[1]) in quarter.month_nums:
                quarter.activity_values.append(int(df_trend[activity_key][i]))
                break;

    activity_dict = {'Date': [], 'Activity': []}
    for quarter in quarter_list:
        quarter.calc_total_activity()
        activity_dict['Date'].append(quarter.quarter_date)
        activity_dict['Activity'].append(quarter.total_activity)

    df_act = pd.DataFrame(activity_dict)

    activity_percent_change = []
    for i in range(len(df_act.index)):
        activity_percent_change.append((df_act['Activity'][i] - df_act['Activity'][0]) / float(df_act['Activity'][0]))

    df_act['Activity_Percent_Change'] = activity_percent_change
    df_act['Date'] = pd.to_datetime(df_act['Date'])
    df_act = df_act.set_index('Date')
    df_act['Activity_Percent_Change'].plot()

    correlation = df_act['Activity_Percent_Change'].corr(df_simfin['Revenue_Percent_Change'])
    print(f'{activity_key}: {correlation}')


plt.legend().remove()
plt.show()


# writer = pd.ExcelWriter('output/output.xlsx', engine='xlsxwriter')
# df.to_excel(writer, sheet_name='output')
# writer.save()
# writer.close()

