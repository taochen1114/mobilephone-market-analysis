#coding=utf-8
# 練習使用 bass diffusion model 做 regression
# 練習 multiprocess 的用法
import math 
import os 
import time
import multiprocessing as mp
from itertools import repeat

def count_mse(p,q,m,t,N):
    sum_error = 0.0
    for i in range(3):
        N_predict = m*((1- math.exp(-1*(p + q)*(t+i))) / (1+ (q/p)*math.exp(-1*(p + q )*(t+i))))
        sum_error += math.pow(N[t]-N_predict, 2)
    return math.sqrt(sum_error/3)

def count_error(p,q,m,t,N):
    N_predict = m*((1- math.exp(-1*(p + q)*(t+1))) / (1+ (q/p)*math.exp(-1*(p + q )*(t+1))))
    error_value = math.sqrt(math.pow(N[t]-N_predict, 2))
    return error_value

# find min error and para
def count_bassmodel_p_q_m_error(start,end,p_value,q_value,m_value, N):
    sum_error = 0
    curr_min_error = 999999999
    param_result = []
    for p_itr in range(start,end,1):
        p = p_value[p_itr]
        for q_itr in range(len(q_value)):
            q = q_value[q_itr]
            for m in m_value:
                sum_error = 0
                # general case
                for t in range(len(N)):
                    N_predict = m*((1- math.exp(-1*(p + q)*(t+1))) / (1+ (q/p)*math.exp(-1*(p + q )*(t+1))))
                    error_value = math.sqrt(math.pow(N[t]-N_predict, 2))
                    sum_error += error_value
                    # sum_error += count_error(p,q,m,t)
                if sum_error < curr_min_error:
                    curr_min_error = sum_error
                    param_result = [p,q,m,t+1]
                    sum_error = 0
                else:
                    sum_error = 0

    return curr_min_error, param_result

def multicore_count_p_q_m_error(p_value,q_value,m_value, N):
    sum_error = 0
    curr_min_error = 999999999
    param_result = []
    for p_itr in range(len(p_value)):
        p = p_value[p_itr]
        for q_itr in range(len(q_value)):
            q = q_value[q_itr]
            for m in m_value:
                sum_error = 0
                # multicore
                pool = mp.Pool()
                result = pool.starmap(count_error, zip(repeat(p),repeat(q),repeat(m),range(len(N)),repeat(N)))
                sum_error = sum(result)
                # general case
                # for t in range(len(N)):
                #     sum_error += count_error(p,q,m,t,N)
                if sum_error < curr_min_error:
                    curr_min_error = sum_error
                    param_result = [p,q,m,len(N)]
                    sum_error = 0
                else:
                    sum_error = 0

    return curr_min_error, param_result

def deep_multicore_count_p_q_m_error(p_value,q_value,m_value, N):
    sum_error = 0
    curr_min_error = 999999999
    param_result = []
    for p_itr in range(len(p_value)):
        p = p_value[p_itr]
        for q_itr in range(len(q_value)):
            q = q_value[q_itr]

            # multicore
            pool = mp.Pool()
            result = pool.starmap(deep_count_error, zip(repeat(p),repeat(q),m_value,repeat(N)))
            
            # 寫法 1
            # temp_min = result[_][0]
            # idx = [idx for idx,j in enumerate(result[idx][0]) if j==temp_min]
            # param_result = result[idx][1]
            # print("temp min = ",temp_min)

            # # 寫法 2
            for i in range(len(result)):
                if result[i][0] < curr_min_error:
                    curr_min_error = result[i][0]
                    param_result = result[i][1]

    return curr_min_error, param_result

def deep_count_error(p,q,m,N):
    curr_min_error = 99999
    sum_error = 0
    for t in range(len(N)):
        N_predict = m*((1- math.exp(-1*(p + q)*(t+1))) / (1+ (q/p)*math.exp(-1*(p + q )*(t+1))))
        error_value = math.sqrt(math.pow(N[t]-N_predict, 2))
        sum_error += error_value
    if sum_error < curr_min_error:
        curr_min_error = sum_error
        param_result = [p,q,m,t+1]
    return [curr_min_error,param_result]

if __name__=='__main__':        
    e = math.e
    print(e)

    error_value = 0
    p_value = []
    q_value = []

    # lab 1
    m_value = [1,1.01,1.02,1.03,1.04,1.05,1.06,1.07,1.08,1.09,1.10,1.11]
    # lab 2
    # m_value = [1,1.01,1.02,1.03,1.04,1.05,1.06,1.07,1.08,1.09,1.10,1.11,1.12,1.13,1.14,1.15]

    # NCCU = [0.0019, 0.0041, 0.0096, 0.0185, 0.0257, 0.0276, 0.0362, 0.0451, 0.0686, 0.2156, 0.5224, 0.8024, 0.9724, 1.083, 1.1441, 1.0031, 0.9737, 1.016, 1.058, 1.103]
    N = [0.0019, 0.0041, 0.0096, 0.0185, 0.0257, 0.0276, 0.0362, 0.0451, 0.0686, 0.2156, 0.5224, 0.8024, 0.9724, 1.083, 1.1441, 1.0031, 0.9737, 1.016, 1.058]

    # 調整
    # N = [0.002145,0.004542,0.009893,0.019413,0.0265,0.0328,0.0525,0.0667,0.1146,0.2156,0.5224,0.6324,0.726056,0.80259,0.840813,0.8331,0.8537,0.906,0.948]
    t = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    print(len(N))
    N_input = []

    #
    for i in range(1000):
        data = float((i+1))/1000.0
        p_value.append(data)

    for i in range(200):
        data = float((i+1))/100.0
        q_value.append(data)
        
    p_length = len(p_value)
    q_length = len(q_value)
    m_length = len(m_value)
    N_length = len(N)
    t_length = len(t)

    # print math.pow(e,2)
    # print math.exp(2)

    result_output = []
    temp_arr = []
    for i in range(3,N_length-3):
        for n in range(i):
            temp_arr.append(N[n])
        N_input.append(temp_arr)
        temp_arr = []

    sum_error = 0
    min_sum_error = 0
    param_result = []

    os.system("""echo 'p, q, m, year, mse' > output.csv""")
    
    start_time = time.time()
    for n in N_input:
        print(n)

        # multicore
        # min_sum_error,param_result = multicore_count_p_q_m_error(p_value,q_value,m_value,n)

        # deep-multicore
        # min_sum_error,param_result = deep_multicore_count_p_q_m_error(p_value,q_value,m_value, n)

        # normal 
        min_sum_error,param_result = count_bassmodel_p_q_m_error(0,10000,p_value,q_value,m_value, n)
        
        print(min_sum_error,param_result)
        p = param_result[0]
        q = param_result[1]
        m = param_result[2]
        t = param_result[3]
        N_predict = m*((1- math.exp(-1*(p + q)*(t+1))) / (1+ (q/p)*math.exp(-1*(p + q )*(t+1))))
        mse = count_mse(p,q,m,t+1,N)
        print('predict:',N_predict)
        print('mse:',mse)
        os.system("""echo \"{}, {}, {}, {}, {}\" >> output.csv""".format(p,q,m,t+1989,mse))
    
    end_time = time.time()
    print('time:',end_time-start_time)
