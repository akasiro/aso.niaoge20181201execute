# -*- coding: utf-8 -*-
import requests, os, csv, time
from bs4 import BeautifulSoup
from getrandomheader import getrandomheader
from ippool import get_random_ip



#1.获取网页
def scrapeweb(appleid,headers,proxies = None):
    #1.1 构造url
    bsurl = 'http://aso.niaogebiji.com/app/baseinfo?id={}'.format(appleid)
    vurl = 'http://aso.niaogebiji.com/app/version?id={}'.format(appleid)
    purl = 'http://aso.niaogebiji.com/app/samepubapp?id={}'.format(appleid)
    #1.2 获取网页
    if proxies is None:
        bres = requests.get(bsurl,headers= headers,timeout = 1)
        time.sleep(2)
        vres = requests.get(vurl,headers = headers,timeout = 1)
        time.sleep(2)
        pres = requests.get(purl,headers = headers,timeout = 1)
    else:
        bres = requests.get(bsurl, headers=headers,proxies = proxies, timeout = 2)
        time.sleep(2)
        vres = requests.get(vurl, headers=headers, proxies = proxies, timeout = 2)
        time.sleep(2)
        pres = requests.get(purl, headers=headers,proxies = proxies, timeout =2)
    return [bres,vres,pres]
#2.解析网页
def parsebres(appleid,res):
    soup = BeautifulSoup(res.text,'html.parser')
    basecontentdiv1 = soup.find('div', class_='appinfoTxt flex1 mobile-hide')
    appName = basecontentdiv1.find('p', class_='appname ellipsis').get_text()
    vdict = {'appType': 'category', 'price': 'price', 'latestVersion': 'version'}
    for key in vdict:
        targetdiv = basecontentdiv1.find('div', class_=vdict[key])
        if targetdiv != None:
            try:
                if key == 'appType':
                    vdict[key] = targetdiv.a.get_text()
                else:
                    vdict[key] = targetdiv.find('div', class_='info').get_text()
            except:
                vdict[key] = ''
        else:
            vdict[key] = ''

    appType = vdict['appType']
    price = vdict['price']
    latestVersion = vdict['latestVersion']

    baseinfotable = soup.find('table', class_='base-info base-area mobile-hide')
    variabledict = {"developerFirm": "开发商", "developer": "开发者", "tags": "分类", "releaseDate": "发布日期",
                    "lastestDate": "更新日期", "bundleId": "Bundle ID", "lastestVer": "版本", "size": "大小",
                    "payInApp": "是否有内购", "support": "支持网站", "compatibility": "兼容性", "lang": "语言", "contentRank": "内容评级"}
    for key in variabledict:
        targettd = baseinfotable.find('td', text=variabledict[key])
        if targettd != None:
            try:
                if key == 'support':
                    variabledict[key] = targettd.next_sibling.a.get_text()
                else:
                    testtd = targettd.next_sibling.next_sibling
                    variabledict[key] = testtd.get_text()
            except:
                variabledict[key] = ''
        else:
            variabledict[key] = ''
    developerFirm = variabledict['developerFirm']
    developer = variabledict['developer']
    tags = variabledict['tags']
    releaseDate = variabledict['releaseDate']
    lastestDate = variabledict['lastestDate']
    bundleId = variabledict['bundleId']
    lastestVer = variabledict['lastestVer']
    size = variabledict['size']
    payInApp = variabledict['payInApp']
    support = variabledict['support']
    compatibility = variabledict['compatibility']
    lang = variabledict['lang']
    contentRank = variabledict['contentRank']

    datalist = [appleid, appName, appType, price, latestVersion, developerFirm, developer, tags, releaseDate, lastestDate,
                bundleId, lastestVer, size, payInApp, support, compatibility, lang, contentRank]


    intro = soup.find('div', class_='vertxt')
    if intro != None:
        introcontent = str(intro).replace('<br>', '').replace('<div class="vertxt" style="max-height: 156px;">',
                                                              '').replace('<div class="vertxt">', '').replace('<br/>',
                                                                                                              '').replace(
            '</div>', '')
    else:
        introcontent = ''
    introfilename = 'intro{}.txt'.format(appleid)
    return [datalist,introcontent,introfilename]
def parsevres(appleid,res):
    soup = BeautifulSoup(res.text, 'html.parser')
    targetdiv = soup.find('div', class_='rankcontent')
    verdivlist = targetdiv.find_all('div', class_='versionItem')
    for verdiv in verdivlist:
        verDate = verdiv.find('div', class_='verDate').get_text()
        versionTitle = verdiv.find('p', class_='versionTitle').get_text()
        versionTitle2 = 'v' + versionTitle
        vertxt = verdiv.find('div', class_='vertxt')
        vercontent = str(vertxt).replace('<div class="vertxt">', '').replace('<br>', '').replace('</div>', '').replace(
            '<br/>', '')
        timeArray = time.strptime(verDate, "%Y年%m月%d日")
        timestamp = time.mktime(timeArray)
        filename = '%sv%s.txt' % (appleid, versionTitle)
        filename = filename.replace('.','_').replace('_txt','.txt')
        datalist = [appleid, verDate, timestamp, versionTitle, versionTitle2, filename]
        yield [datalist,vercontent,filename]

def parsepres(appleid,res):
    soup = BeautifulSoup(res.text, 'html.parser')
    samepubapp = soup.find('div',{'id':'samepubapp'})
    artistname = soup.find('div', {'class': 'artistnamezh'}).get_text()
    table = samepubapp.find('tbody')
    if table is None:
        samepubappnum =0
        samepubapplist = " "
        samepubapplistid = " "
    else:
        tr = table.find_all('tr')
        samepubappnum = len(tr)
        samepubapplist = []
        samepubappidlist = []
        for t in tr:
            ainfo = t.find('a',{'class':'app_name'})
            sameappid = ainfo['href'].replace('/app/weekdatareport?id=','')
            sameappname = ainfo.get_text().replace(',','')
            samepubapplist.append(sameappname)
            samepubappidlist.append(sameappid)
        samepubapplist = '|'.join(samepubapplist)
        samepubapplistid = '|'.join(samepubappidlist)
    data = [appleid, artistname, samepubappnum, samepubapplist, samepubapplistid]

    return data



#3.存储数据
#3.1 结构化数据
def saveascsv(datalist, filepath):
    with open(filepath,'a+',newline= '',encoding= 'utf-8') as csvfile:
        w = csv.writer(csvfile)
        w.writerow(datalist)
    time.sleep(0.25)

def saveastxt(content,filepath):
    if content != '':
        with open(filepath,'a+',encoding='utf-8') as txtfile:
            txtfile.write(content)
        time.sleep(0.25)

#4.爬虫主程序
def main():
    appleidlistpath = 'input/appleid2017.txt'
    usedidpath = 'tool/usedid.txt'
    erroridpath = 'tool/errorid.txt'
    baseinfocsvpath = os.path.join(os.path.dirname(os.getcwd()),'data','baseinfo.csv')
    versioncsvpath = os.path.join(os.path.dirname(os.getcwd()),'data','version.csv')
    publishcsvpath = os.path.join(os.path.dirname(os.getcwd()),'data','publisher.csv')
    updatepath = os.path.join(os.path.dirname(os.getcwd()),'data','update')
    intropath = os.path.join(os.path.dirname(os.getcwd()),'data','intro')
    proxies = get_random_ip()
    for appleid in txt2list(appleidlistpath):
        if appleid in txt2list(usedidpath) or appleid in txt2list(erroridpath):
            continue
        try:
            reslist = scrapeweb(appleid,headers=getrandomheader(),proxies=proxies)
            parseb= parsebres(appleid,reslist[0])
            parsev= parsevres(appleid,reslist[1])
            parsep = parsepres(appleid,reslist[2])
            saveascsv(parseb[0],baseinfocsvpath)
            saveastxt(parseb[1],os.path.join(intropath,parseb[2]))
            for ver in parsev:
                saveascsv(ver[0],versioncsvpath)
                saveastxt(ver[1],os.path.join(updatepath,ver[2]))
            saveascsv(parsep,publishcsvpath)

            with open('tool/usedid.txt','a+') as f:
                f.write('\n{}\n'.format(appleid))
            print('success : {}'.format(appleid))
            time.sleep(2)
        except:
            print('error : {}'.format(appleid))
            with open('tool/errorid.txt','a+') as f2:
                f2.write('\n{}\n'.format(appleid))
            proxies = get_random_ip()
            time.sleep(15)
            continue

        #break




#5. 辅助应用
#5.1 txt转list
def txt2list(filepath):
    with open(filepath,'r') as f:
        templist = [i.replace('\n','') for i in f.readlines()]
    return  templist

if __name__ == '__main__':
    main()

