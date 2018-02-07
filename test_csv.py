#coding=utf-8
import csv

def save_to_report(row_data):
    with open('report.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar=',', quoting=csv.QUOTE_MINIMAL) # 逗號分隔
        writer.writerow(['FileName', 'Supply And Sale Ratio Threshold', 'Supply And Sale Bounce Ratio Threshold', 'Big Supply in 7 Days Threshold', '1st Low Supply-Sale Ratio Point(days)', 'Hardcore Point(days)', 'Hardcore'])
        for row in row_data:
            writer.writerow(row)

row_data = [['iPhone6.csv',0.033, 0.02, 1000 ,361, 361, 278906], 
        ['iPhone6_Plus.csv',0.033, 0.02, 1000 ,361, 361, 278906],
        ['iPhone6s.csv',0.033, 0.02, 1000 ,361, 361, 278906],
        ['iPhone7.csv',0.033, 0.02, 1000 ,361, 361, 278906]]

save_to_report(row_data)