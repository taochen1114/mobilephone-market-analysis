#coding=utf-8
import multiprocessing as mp
from itertools import repeat
import numpy as np

# 我們想要在 multiprocess 中執行以下多參數的 function
def count_error(p,q,m,t,N):
    print('in func:',p,q,m,t,N)
    return p + N[t]

if __name__=='__main__':
    a = [1,2]
    b = [3,4]

    # 這樣寫只能印出物件的記憶體位置
    print(zip(a,b)) # <zip object at 0x1026ad148>
    # 這樣寫才能看到內容
    print(list(zip(a,b))) # [(1, 3), (2, 4)]

    for i,j in zip(a,b): 
        print(i,j)
        '''output:
            1 3
            2 4
        '''
    # 當 a, b 數量一樣的時候 zip 會幫你一對一對起來
    # 但是當 a, b 數量不同的時候怎麼辦呢？
    # 例如 a 是個 list, b 只是一個數字
    a = [1,2,3]
    b = 4
    # 使用迭代工具 repeat 來自動幫 b 值做 repeat 
    print(list(zip(a,repeat(b)))) # [(1, 4), (2, 4), (3, 4)]

    # 又或者我們要把 a,b,c 三個參數組合，拿去跟一個從零開始逐步加一成長中的數字一起迭代計算
    a = 1
    b = 2
    c = [3.14,2.7183,0.009]
    for i,j,k,l in zip(repeat(a),repeat(b),repeat(c),range(3)):
        print(i,j,k,l)
    '''output
    1 2 [3.14, 2.7183, 0.009] 0
    1 2 [3.14, 2.7183, 0.009] 1
    1 2 [3.14, 2.7183, 0.009] 2
    '''

    p = 1
    q = 2
    m = 3
    N = [0.2,0.3,0.4,0.5]

    # 使用 zip 搭配 repeat 工具可以將所有參數組合好 目前 range(len(N)) 的部分是想要 iteration 的重點項目
    print('zip:',list(zip(repeat(p),repeat(q),repeat(m),range(len(N)),repeat(N))))
    ''' 印出的 zip 長這樣:
    zip: [(1, 2, 3, 0, [0.2, 0.3, 0.4, 0.5]), (1, 2, 3, 1, [0.2, 0.3, 0.4, 0.5]), 
          (1, 2, 3, 2, [0.2, 0.3, 0.4, 0.5]), (1, 2, 3, 3, [0.2, 0.3, 0.4, 0.5])]
    '''

    # 使用 pool 
    pool = mp.Pool()
    # 使用 starmap 加上 zip 可以支援多參數傳遞，並可以接到 function 的 reutrn 值
    res = pool.starmap(count_error, zip(repeat(p),repeat(q),repeat(m),range(len(N)),repeat(N)))
    ''' 執行 count_error 的過程
    in func: 1 2 3 0 [0.2, 0.3, 0.4, 0.5]
    in func: 1 2 3 1 [0.2, 0.3, 0.4, 0.5]
    in func: 1 2 3 2 [0.2, 0.3, 0.4, 0.5]
    in func: 1 2 3 3 [0.2, 0.3, 0.4, 0.5]
    '''
    print('result:',res)       # result: [1.2, 1.3, 1.4, 1.5]
    print('sum = ',sum(res))   # sum =  5.4

