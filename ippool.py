# -*- coding: utf-8 -*-

'''
直接使用proxy = get_random_ip()就可以了
'''
from bs4 import BeautifulSoup
import requests
import random
import json
import time
from getrandomheader import getrandomheader

DefaultHeader = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

def get_ip_list(url ='http://www.xicidaili.com/wn/', headers = DefaultHeader):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].get_text() + ":" + tds[2].get_text())
    return ip_list
def get_qiyeip_list():
    r = requests.get('http://127.0.0.1:8000/?types=0&county=国内')
    ip_ports= json.loads(r.text)
    ip_list = []
    for ipport in ip_ports:
        ip_list.append('{}:{}'.format(ipport[0],ipport[1]))
    return ip_list
def get_random_ip(ip_list = get_qiyeip_list(),testNet = 'http://aso.niaogebiji.com'):
    global DefaultHeader
    headers = DefaultHeader
    while True:
        if len(ip_list) ==0:
            ip_list = get_qiyeip_list()
            headers = getrandomheader()
        randomip = ip_list[random.randint(0,len(ip_list)-1)]
        pro = 'http://{}'.format(randomip)
        proxies = {'http': pro,
                   'https':pro}
        #print(randomip)
        

        try:
            res = requests.get(testNet,headers = headers,proxies = proxies)
        
            if res.status_code == 200:
                res.close()
                break
            else:
                ip_list.remove(randomip)
                res.close()
        except:
            ip_list.remove(randomip)
            time.sleep(0.1)
    #print(proxies)
    return proxies
        

if __name__ == '__main__':
    url = 'http://aso.niaogebiji.com/'
    header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    iplist = ['116.77.205.209:8118']
    proxy = get_random_ip(testNet=url)
    print(proxy)
    #r = requests.get('https://www.baidu.com',proxies = proxy)
    #print(r.status_code)
    #print(get_qiyeip_list())
