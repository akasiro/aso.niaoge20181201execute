# -*- coding: utf-8 -*-
import requests, os, csv, time
from getrandomheader import getrandomheader
from bs4 import BeautifulSoup
from ippool import get_random_ip


#构建url
def genurl(appid,type = 1):
    '''

    :param type:1: baseinfo
    1: baseinfo
    2: version
    :return:
    '''
    #明确url类型
    if type == 1:
        typekey = 'baseinfo'
    elif type == 2:
        typekey = 'version'
    #构造url
    url = 'http://aso.niaogebiji.com/app/{}?id={}'.format(typekey,appid)
    return url

def getdata(appid,proxy):
    appidused = txt2list('tool/usedid.txt')
    if appid not in appidused:
        getversion(appid,proxy)
        logandprint('success: {}'.format(appid))
        with open('tool/usedid.txt','a+') as f:
            f.write(appid+'\n')
    else:
        logandprint('already: {}'.format(appid))


def getbaseinfo(appid,proxy):
    burl = genurl(appid,1)
    usedurl = txt2list('tool/usedurl.txt')
    if burl not in usedurl:
        if proxy == {}:
            res = requests.get(burl, headers=getrandomheader())
        else:
            res = requests.get(burl,headers = getrandomheader(), proxies = proxy)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text,'html.parser')
            basecontentdiv1 = soup.find('div',class_ = 'appinfoTxt flex1 mobile-hide')
            appName = basecontentdiv1.find('p',class_ = 'appname ellipsis').get_text()
            vdict = {'appType':'category','price':'price','latestVersion':'version'}
            for key in vdict:
                targetdiv = basecontentdiv1.find('div',class_ = vdict[key])
                if targetdiv != None:
                    try:
                        if key == 'appType':
                            vdict[key] = targetdiv.a.get_text()
                        else:
                            vdict[key] = targetdiv.find('div',class_ = 'info').get_text()
                    except:
                        vdict[key] = ''
                else:
                    vdict[key] = ''

            appType = vdict['appType']
            price = vdict['price']
            latestVersion = vdict['latestVersion']

            baseinfotable = soup.find('table',class_ = 'base-info base-area mobile-hide')
            variabledict = {"developerFirm":"开发商", "developer":"开发者", "tags":"分类", "releaseDate":"发布日期", "lastestDate":"更新日期", "bundleId":"Bundle ID", "lastestVer":"版本", "size":"大小", "payInApp":"是否有内购", "support":"支持网站", "compatibility":"兼容性", "lang":"语言", "contentRank":"内容评级"}
            for key in variabledict:
                targettd = baseinfotable.find('td',text = variabledict[key])
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

            datalist = [appid,appName,appType,price,latestVersion,developerFirm,developer,tags,releaseDate,lastestDate,bundleId,lastestVer,size,payInApp,support,compatibility,lang,contentRank]
            recordcsv('baseinfo',datalist)

            intro = soup.find('div',class_ = 'vertxt')
            if intro != None:
                introcontent = str(intro).replace('<br>','').replace('<div class="vertxt" style="max-height: 156px;">','').replace('<div class="vertxt">','').replace('<br/>','').replace('</div>','')
            else:
                introcontent = ''

            recorddata(appid,introcontent)

            logandprint('stagesuccess: baseinfo {}'.format(appid))
            with open('tool/usedurl.txt','a+') as f:
                f.write('\n'+burl)

            res.close()
            time.sleep(10)

    else:
        logandprint('already: baseinfo {}'.format(appid))

def getversion(appid, proxy):
    vurl = genurl(appid,2)
    usedurl = txt2list('tool/usedurl.txt')
    if vurl not in usedurl:
        if proxy == {}:
            res = requests.get(vurl, headers=getrandomheader())
        else:
            res = requests.get(vurl,headers = getrandomheader(), proxies = proxy)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            targetdiv = soup.find('div',class_ = 'rankcontent')
            verdivlist = targetdiv.find_all('div',class_ = 'versionItem')
            for verdiv in verdivlist:
                verDate = verdiv.find('div',class_ = 'verDate').get_text()
                versionTitle = verdiv.find('p',class_ = 'versionTitle').get_text()
                versionTitle2 = 'v'+versionTitle
                vertxt = verdiv.find('div', class_ = 'vertxt')
                vercontent = str(vertxt).replace('<div class="vertxt">','').replace('<br>','').replace('</div>','').replace('<br/>','')
                timeArray = time.strptime(verDate, "%Y年%m月%d日")
                timestamp = time.mktime(timeArray)
                filename = 'update/%sv%s.txt' % (appid, versionTitle)
                datalist = [appid,verDate,timestamp,versionTitle,versionTitle2,filename]
                recordcsv('versionwithfilename',datalist)
                #recorddata(appid,vercontent,versionTitle)

            logandprint('stagesuccess: version {}'.format(appid))

            with open('tool/usedurl.txt', 'a+') as f:
                f.write('\n' + vurl)

            res.close()
            time.sleep(5)


    else:
        logandprint('already: version {}'.format(appid))


#记录
def logandprint(str):
    print(str)
    with open('tool/log.txt','a+') as f:
        f.write(str+'\n')



#txt转list
def txt2list(filename):
    with open(filename,'r') as f:
        temp = f.readlines()
    templist = []
    for t in temp:
        templist.append(t.replace('\n',''))
    return  templist

#初始化文件夹和usedlist
def initialtoolandpath():
    for pathname in ['tool','data','data/intro','data/update']:
        if not os.path.exists(pathname):
            os.makedirs(pathname)
    for toolfile in ['usedid.txt','usedurl.txt']:
        if not os.path.exists('tool/'+toolfile):
            with open('tool/'+toolfile,'a+') as f:
                f.write('')
#记录文本数据
def recorddata(gameid,content,version=''):
    gameid = str(gameid)
    if version == '':
        filename = 'data/intro/%sintro.txt'%gameid
    else:
        version = version.replace('.','_')
        filename = 'data/update/%sv%s.txt'%(gameid,version)
    with open(filename, 'w',encoding='utf-8') as f:
        f.write(gameid)
        f.write('\n')
        f.write(content)
#记录非文本数据
def recordcsv(filename,datalist):
    filename = 'data/%s.csv'%filename
    with open(filename,'a+',newline='',encoding='utf-8') as f:
        mywriter = csv.writer(f)
        mywriter.writerow(datalist)

def main():
    initialtoolandpath()
    appidlists = txt2list('usedid2.txt')
    usedid = txt2list('tool/usedid.txt')
    proxy = get_random_ip(testNet='http://aso.niaogebiji.com/')
    #proxy = {}
    while len(usedid) < len(appidlists):
        logandprint('loop start')
        for appid in appidlists:
            try:
                getdata(appid,proxy)
            except:
                logandprint('something wrong {}'.format(appid))
                proxy = get_random_ip(testNet='http://aso.niaogebiji.com/')
                #proxy = {}
                time.sleep(5)
        usedid = txt2list('tool/usedid.txt')
        time.sleep(300)
    logandprint('mission complete')




if __name__ == '__main__':
    main()
    # getdata(appid)
    # initialtoolandpath()
    # getbaseinfo(appid)
    # getversion(appid)