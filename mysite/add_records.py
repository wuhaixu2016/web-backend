import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()

from news.models import New
from news.script.regularization import *

def analyseHtml(url, id = 0):
    result = htmlSpider(url, id)
    tmpDate = match(result)
    if tmpDate is None:
        tmpDate = ''

    result = result[result.find("<body>"):result.find("</body>")+7]
    # 先清洗script
    result = removeTag(result, '<script', '</script>')
    # 再清洗<!-- -->
    result = removeTag(result, '<!--', '-->')
    # 再清洗style
    result = removeTag(result, '<style', '</style>')

    # 最后清洗标签，给文字后面添加换行符
    tmp1 = result.split('<')
    for i in range(len(tmp1)):
        p = tmp1[i].split('>')
        if(len(p) > 1):
            tmp1[i] = p[1].strip()
            if(len(tmp1[i])>0):
                tmp1[i] += '\n'
        else:
            tmp1[i] = ''
    res = ''
    for i in range(len(tmp1)):
        res += tmp1[i]
    # 保存文件
    n = New(news_title = ((res.split('\n'))[0]), news_date = tmpDate, news_url = url, news_text = res)
    n.save()

def getContext(path):
    count = 0
    th = []
    u = open(path, 'r')
    for line in u:
        count+=1
        line = line[:len(line)-1]
        print(count)
        tmp = threading.Thread(target = analyseHtml, args=(line,count,))
        th.append(tmp)
        th[count-1].start()
    for i in range(len(th)):
        th[i].join()
    u.close()

if __name__ == '__main__':
    getContext('./news/script/url.txt')

