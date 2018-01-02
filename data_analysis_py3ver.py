# coding=UTF-8
import csv
import numpy as np
import matplotlib.pyplot as plt
# from string import maketrans
import sys
import shutil
import os

'''
0 day                               累計銷售日 1 2 3
1 WeekDay                           星期幾 Mon Tue Wed 
2 Date                              日期 2017-03-24
3 Sale                              銷貨 999999
4 Purchase                          進貨
5 SellBack                          銷退
6 DailyPurchase                     當日進貨
7 EndingInventory                   期末庫存 
8 BeginingInventory                 期初庫存
9 SaleMovingMean7Day                七日均銷
10 TotalSale                        總銷量
11 SupplyAndSaleRatio_MovingMean    供銷比移動平均
12 SupplyAndSaleRatio               供銷比
'''

INPUT_FILE_NAME_ARR = ['iPhone3GS.csv','iPhone4.csv','iPhone4s.csv','iPhone5.csv','iPhone5s.csv','iPhone6.csv','iPhone6_Plus.csv','iPhone6s.csv','iPhone6s_Plus.csv','iPhone7.csv','iPhone7_Plus.csv']

# INPUT_FILE_NAME = 'iPhone4s_modify.csv'+++
INPUT_FILE_NAME = 'iPhone4s.csv'

# 當供銷比低於 0.05 (20天) 或 0.033(30天)
SAS_RATIO_THRESH = 0.033

# 反彈幅度的 threshold
SAS_BOUNCE_RATIO_THRESH = 0.02

# 大量供貨與目前銷貨的移動平均倍數關係為五倍
BIG_SUPPLY_FACTOR = 5

# 單日大銷量的門檻值 預設 1000台
BIG_DAILY_SALE_THRESH = 1000

# 七日均銷大銷量門檻值 1000
BIG_WEEKLY_SALE_THRESH = 1000

# 銷量大筆回升門檻 1500
BIG_WEEKDAY_SALE_BOUNCE_THRESH = 1500

# 2009 ~ 2014 年假期間都不列入資料分析計算！
NEW_YEAR_FACTOR = ['2009-01-25', '2009-01-26', '2009-01-27', '2009-01-28', '2009-01-29', '2009-01-30', '2009-01-31', 
                    '2010-02-13', '2010-02-14', '2010-02-15', '2010-02-16', '2010-02-17', '2010-02-18', '2010-02-19', '2010-02-20',
                    '2011-02-02', '2011-02-03', '2011-02-04', '2011-02-05', '2011-02-06', '2011-02-07', '2011-02-08', 
                    '2012-01-21', '2012-01-22', '2012-01-23', '2012-01-24', '2012-01-25', '2012-01-26', '2012-01-27', '2012-01-28', 
                    '2013-02-09', '2013-02-10', '2013-02-11', '2013-02-12', '2013-02-13', '2013-02-14', '2013-02-15', '2013-02-16', '2013-02-17', 
                    '2014-01-30', '2014-01-31', '2014-02-01', '2014-02-02', '2014-02-03', '2014-02-04', '2014-02-05', 
                    '2015-02-17', '2015-02-18', '2015-02-19', '2015-02-20', '2015-02-21', '2015-02-22', '2015-02-23', 
                    '2016-02-06', '2016-02-07', '2016-02-08', '2016-02-09', '2016-02-10', '2016-02-11', '2016-02-12', '2016-02-13', 
                    '2017-01-27', '2017-01-28', '2017-01-29', '2017-01-30', '2017-01-31', '2017-02-01', '2017-02-02', '2017-02-03', '2017-02-04']

# 輸出模式 
#  1: 7DaysSaleMovingMean
#  2: TotalSale
OUTPUT_MODE = 1

# 整理後欲分析的資料 list
data_arr = []
# 繪圖用的 x 軸資料
x_arr = []
# 繪圖用的 y 軸資料
y_arr = []
# 我們要找的 hardcore 切斷的時間點
hardcore_cut_point = 0


def is_chinese_new_year(date):
    if any(date in s for s in NEW_YEAR_FACTOR):
        return True
    else:
        return False

def read_data_to_arr(reader):
    my_data_arr = []
    i = 0
    counter = 0
    # 讀取並整理資料
    for row in reader:
        tmp = ', '.join(row)
        if counter == 0:
            print(tmp)
            counter += 1
        else:
            tmp_arr = tmp.split(',')
            my_data_arr.append(tmp_arr)
            i += 1

    return my_data_arr

def check_week_saleratio_bounce(current_counter, data_arr, week_arr):
    j = 0
    flag = False
    while j < 7:
        if (current_counter+j < len(data_arr)):
            bounce_data1 = data_arr[current_counter+j]
            if (current_counter+j+1 < len(data_arr)):
                bounce_data2 = data_arr[current_counter+j+1]

                # 有反彈，且反彈幅度"夠大" 大於 SAS_BOUNCE_RATIO_THRESH 
                if float(bounce_data2[12]) > float(bounce_data1[12]) + SAS_BOUNCE_RATIO_THRESH:
                    # print bounce_data1
                    # print bounce_data2
                    # print "UPPPPPPPPPPPPPPP!!!!!!"
                    flag = True
                # else:
                    # print bounce_data1
                    # print bounce_data2
                    # print "Downnnnnnnnnnnnn!!!!!"
                    
            week_arr.append(data_arr[current_counter+j])
        j += 1

    return flag, week_arr

'''
    funcion name: check_week_daily_big_supply
    input:
        week_arr: 一週資料
        BIG_SUPPLY_FACTOR: 大的供貨與七日均銷的倍數關係
    output:
        True: 一週內有大供貨
        Fals: 一週內有無大供貨
'''
def check_week_daily_big_supply(week_arr, BIG_SUPPLY_FACTOR=BIG_SUPPLY_FACTOR):
    flag = False
    for data in week_arr:
        # 供貨量大於七日均銷的五倍
        if float(data[4]) > float(data[9]) * BIG_SUPPLY_FACTOR:
            flag = True
    return flag

'''
    funcion name: check_week_daily_big_sale
    input:
        week_arr: 一週資料
        BIG_DAILY_SALE_THRESH: 大的日銷量門檻值
    output:
        True: 一週內有大日銷量出現
        Fals: 一週內有無大日銷量出現
'''
def check_week_daily_big_sale(week_arr, BIG_DAILY_SALE_THRESH=BIG_DAILY_SALE_THRESH):
    flag = False
    for data in week_arr:
        # 單日銷量破千 就算是單日有大銷量
        if float(data[3]) > BIG_DAILY_SALE_THRESH:
            flag = True
    return flag

def check_week_low_supply_condition(week_arr, BIG_WEEKLY_SALE_THRESH=BIG_WEEKLY_SALE_THRESH, BIG_WEEKDAY_SALE_BOUNCE_THRESH=BIG_WEEKDAY_SALE_BOUNCE_THRESH):
    flag = False

    for data in week_arr:
        # 七日均銷大於 1000 或 一周內有反彈 1500台
        if (float(data[9]) > BIG_WEEKLY_SALE_THRESH) or check_week_daily_big_sale(week_arr, BIG_WEEKDAY_SALE_BOUNCE_THRESH):
            flag = True

    return flag

def main():
    first_sas_downward_point = 0
    is_first_point = True
    hardcore_point = 0
    find_hardcore = False
    # 讀取資料
    with open(INPUT_FILE_NAME, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

        # 讀取並整理資料
        data_arr = read_data_to_arr(reader)

    # 忽略過年年假
    data_arr = [data for data in data_arr if not is_chinese_new_year(data[2])]
    print('data_arr len', len(data_arr))

    # 檢查資料目前走到哪裡了，避免資料到底的時候出現超出去的危險
    counter = 0 
    for data in data_arr:
        # data[0] 目前的銷售天數
        x = float(data[0])

        if OUTPUT_MODE == 1:  # data[9] 目前的七日均銷
            y = float(data[9]) # SaleMovingMean7Day
        if OUTPUT_MODE == 2:  # data[10] 目前的總銷量
            y = float(data[10]) # TotalSale

        # # 忽略過年年假r double check
        # if is_chinese_new_year(data[2]):
        #     print("Happy New Year!", data[2])
        #     continue
        
        # 開始有銷售
        if float(data[10]) > 0.0:
            # print "XD"
            print(data[2])
            # 倘若供銷比 低於一定比例時 < 0.05 也就是低於庫存 20 天 or 0.033 (30天)
            if float(data[12]) < SAS_RATIO_THRESH:
                # print "--------------- DATA ---------------"
                # print data

                # 觀察一週是否反彈
                week_arr = []

                if (counter+6 < len(data_arr)):
                    is_saleratio_bounce, week_arr = check_week_saleratio_bounce(counter, data_arr, week_arr)

                    # 檢查一週內有大量供貨 T: 有  F: 無
                    is_big_supply_in_week = check_week_daily_big_supply(week_arr)

                    # 檢查一週內是否有大的日銷量 T: 有  F: 無
                    is_big_sale_in_week = check_week_daily_big_sale(week_arr)
                    
                    # 檢查一週內均銷量與日銷量是否還有回彈 T: 有 F 無
                    is_low_supply_bounce_condition_in_week = check_week_low_supply_condition(week_arr)

                    # 供銷比沒有反彈
                    if is_saleratio_bounce == False:
                        print(week_arr)
                        print(is_saleratio_bounce)
                        print(is_big_supply_in_week)
                        print(is_big_sale_in_week)
                        print(is_low_supply_bounce_condition_in_week)

                        # 找到第一個供銷比連續下降點
                        if is_first_point:
                            first_sas_downward_point = int(x)
                            is_first_point = False

                        if not find_hardcore:
                            # 無大量供貨
                            if is_big_supply_in_week == False:
                                if is_low_supply_bounce_condition_in_week == False:
                                    hardcore_point = counter
                                    find_hardcore = True

                            # 有大量供貨 且 日銷量均為 1000 以下 
                            if is_big_supply_in_week == True and is_big_sale_in_week == False:
                                if is_low_supply_bounce_condition_in_week == False:
                                    hardcore_point = int(x)
                                    find_hardcore = True

            x_arr.append(x)
            y_arr.append(y)

        counter += 1

    save_figure(x_arr, y_arr, first_sas_downward_point, hardcore_point)

def find_hardcore(hardcore_point):
    # 讀取資料
    with open(INPUT_FILE_NAME, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

        # 讀取並整理資料
        data_arr = read_data_to_arr(reader)
    return data_arr[hardcore_point-1][10]
    
def save_figure(x_arr, y_arr, first_sas_downward_point, hardcore_point):
    w,h = plt.figaspect(0.6)
    plt.figure(figsize=(w,h))

    # plt.plot(x_arr, y_arr)
    plt.suptitle(INPUT_FILE_NAME[:-4], fontsize=24)
    # plt.text(1.1,2.0,"供銷比過低門檻:{}".format(SAS_RATIO_THRESH),fontdict=None)
    plt.figtext(0.01, 0.95,'1st low supply-sale ratio at #{} days\n'.format(first_sas_downward_point), horizontalalignment='left', verticalalignment='center', color='red')
    plt.figtext(0.01, 0.95,'\nhardcore at #{} days'.format(hardcore_point), horizontalalignment='left', verticalalignment='center', color='green')

    plt.figtext(0.99, 0.95,'low supply-sale ratio threshold: {}\nbounce ratio threshold: {}\n'.format(SAS_RATIO_THRESH, SAS_BOUNCE_RATIO_THRESH), horizontalalignment='right', verticalalignment='center')
    plt.figtext(0.99, 0.95,'\n\nhardcore: {}'.format(find_hardcore(hardcore_point)), horizontalalignment='right', verticalalignment='center', color='green')
    # plt.figtext(0.99, 0.95,'low supply-sale ratio threshold: {}\nbounce ratio threshold: {}\nhardcore at sale days: {}'.format(SAS_RATIO_THRESH, SAS_BOUNCE_RATIO_THRESH, hardcore_point), horizontalalignment='right', verticalalignment='center')

    plt.plot(x_arr, y_arr,linewidth=2.0)
    plt.axvline(first_sas_downward_point, color='r')
    plt.axvline(hardcore_point, color='g')
    if OUTPUT_MODE == 1:        
        # plt.ylabel(u'七日均銷')
        plt.ylabel('7 Days Sale Moving Mean')
    if OUTPUT_MODE == 2:
        plt.ylabel('Total Sale')

    # plt.xlabel(u'銷售天數')
    plt.xlabel('Sale Days')
    if OUTPUT_MODE == 1:
        plt.savefig(INPUT_FILE_NAME[:-4]+"-7DaysSaleMovingMean.png") # 7 Days Sale Moving Mean 
    if OUTPUT_MODE == 2:
        plt.savefig(INPUT_FILE_NAME[:-4]+"-TotalSale.png") # Total Sale
    
    # plt.imsave(INPUT_FILE_NAME[:-4]+".png")
    plt.show()
    plt.cla()
    plt.clf()
    plt.close()

def global_var(fname, mode, sas_ratio=0.033, sas_bounce_ratio=0.01):
    global INPUT_FILE_NAME
    INPUT_FILE_NAME = fname
    global OUTPUT_MODE
    OUTPUT_MODE = mode

    # 當供銷比低於 0.05 (20天) 或 0.033(30天)
    global SAS_RATIO_THRESH
    SAS_RATIO_THRESH = sas_ratio

    # 反彈幅度的 threshold
    global SAS_BOUNCE_RATIO_THRESH
    SAS_BOUNCE_RATIO_THRESH = sas_bounce_ratio

def move_result_to_folder(fname, sas_ratio=0.033, sas_bounce_ratio=0.01):
    folder_str = r'output/'
    # print(folder_str)
    folder_str = folder_str+str(sas_ratio).replace('.','')+'_'+str(sas_bounce_ratio).replace('.','')+'/'
    print("output folder: {}".format(folder_str))
    shutil.move(fname, folder_str)
    # cmd = 'mv '+fname+' '+folder_str

if __name__ == "__main__":
    # INPUT_FILE_NAME_ARR = ['iPhone3GS.csv','iPhone4.csv','iPhone4s.csv','iPhone5.csv','iPhone5s.csv','iPhone6.csv','iPhone6_Plus.csv','iPhone6s.csv','iPhone6s_Plus.csv','iPhone7.csv','iPhone7_Plus.csv']

    iPhone_Type = input("""input iPhone Type: 
        0: iPhone3GS
        1: iPhone4
        2: iPhone4s
        3: iPhone5
        4: iPhone5s
        5: iPhone6
        6: iPhone6_Plus
        7: iPhone6s
        8: iPhone6s_Plus
        9: iPhone7
        10: iPhone7_Plus\n""")

    fname = INPUT_FILE_NAME_ARR[int(iPhone_Type)]
    print('we will analysis this file:')
    print(fname)

    mode_input = input("""input analysis mode: 
        1: Seven Days Sale Moving Mean
        2: Total Sale\n""")

    mode = int(mode_input)
    
    sas_ratio_input = input('Input Supply And Sale Ratio Threshold (0.033 or 0.05): ')
    sas_ratio = float(sas_ratio_input)
    sas_bounce_ratio_input = input('Input Supply And Sale Bounce Ratio Threshold (0.01 or 0.02): ')
    sas_bounce_ratio = float(sas_bounce_ratio_input)
    global_var(fname,mode,sas_ratio,sas_bounce_ratio)
    # global_var(fname,mode)

    message_str = ['Seven Days Sale Moving Mean Analysis', 'Total Sale Analysis']
    print("\n"+INPUT_FILE_NAME+" in "+message_str[OUTPUT_MODE-1]+" Start!!!")
    print("SAS_RATIO_THRESH = {}, SAS_BOUNCE_RATIO_THRESH = {}".format(SAS_RATIO_THRESH, SAS_BOUNCE_RATIO_THRESH))
    main()

    # move result file to lab result folder (start)
    if OUTPUT_MODE == 1:
        save_fname = INPUT_FILE_NAME[:-4]+"-7DaysSaleMovingMean.png" #7DaysSaleMovingMean 
    if OUTPUT_MODE == 2:
        save_fname = INPUT_FILE_NAME[:-4]+"-TotalSale.png"  # TotalSale

    move_result_to_folder(save_fname, SAS_RATIO_THRESH, SAS_BOUNCE_RATIO_THRESH)
    # os.system(move_result_to_folder(save_fname))
    # move result file to lab result folder (end)


