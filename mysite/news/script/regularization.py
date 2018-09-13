import jieba
import os
import re
import pickle
from bs4 import BeautifulSoup
import importlib,sys
import threading
import requests

def removeTag(result, start, end):
    while(1):
        s = result.find(start)
        if s != -1:
            tmp = result[:(s)]
            tmp += result[result.find(end)+len(end):]
            result = tmp
        else:
            break
    return result

def htmlSpider(url, id = 0):
    result = ''
    try:
        res = requests.get(url)
        result = res.text
    except:
        print('disconnect')
    return result
# get html context
def match(str):
    m = re.search("\d+[-/]\d+[-/]\d+",str)
    if m is None:
        return None
    else:
        return m.group()

if __name__ == '__main__':
    getContext('url.txt')

# find date



# path = 'res/6.txt'
# u = open(path, 'rb')
# f = open('test.txt','w')

# for line in u:
#     seg_list = jieba.cut_for_search(line)
#     str = ','
#     f.write(str.join(seg_list))
#     f.write('\n')

# u.close()
# f.close()