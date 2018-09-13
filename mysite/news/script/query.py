import pickle
import os
import re
import math
import jieba
import threading
from regularization import match

def loadData(path):
	data = []
	for file in os.listdir(path):
		f = open(path+'/'+file,'rb')
		s = pickle.load(f)
		data.append(s)
		f.close()
	return data

def findTop(res, k):
	# for positive number
	r = []
	for i in range(k):
		r.append(res.index(max(res)))
		res[r[i]] = -1
	return r



if __name__ == '__main__':
	data = loadData('./res')
	while(1):
		str = input("请输入查询内容(ctrl+C结束查询)：")
		if match(str) is not None:
			str = re.sub('[-/]','-',str)
			strList = str.split('-')
			if(strList[1][0] == '0'):
				strList[1] = strList[1][1]
			if(strList[2][0] == '0'):
				strList[2] = strList[2][1]
			s = '-'
			s = s.join(strList)
			print("查询结果如下:(日期："+s+')')
			for i in range(len(data)):
				if(data[i][1] == s):
					print(data[i][2],':',data[i][0])
		else:
			seg_list = jieba.cut_for_search(re.sub('[，。？！“”：、《》（）【】]','',str))
			s = ','
			s = s.join(seg_list)
			seg_list = s.split(',')
			res = []
			for i in range(len(data)):
				res.append(0)
				for j in range(len(seg_list)):
					res[i] += data[i][3].count(seg_list[j])
			result = findTop(res,3)
			print('查询结果如下：')
			for i in range(len(result)):
				print(data[result[i]][2],':',data[result[i]][0])
