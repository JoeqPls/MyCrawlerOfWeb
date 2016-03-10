#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-  
# __author__ = Goodweather Fu

from bs4 import BeautifulSoup
import requests, urllib, os, re, time

# cookie and user-agent copy from the website
headers = {
    'Cookie': 'beacon_visit_count=82; pgv_pvi=6575921152; pgv_si=s2681645056; qdgg=2501%3B%3B; stat_gid=7853041686; stat_sessid=25716409859; stat_id24=0,-1,noimg; b_t_s=s; beacon_visit_count=2; rcr=3676417; bc=3676417; qdgd=1; isBindWeiXin=0; lrbc=3676417%7C91812435%7C0; isCloseQDCode=1; __utmt=1; __utma=1.249226873.1457441532.1457441532.1457441532.1; __utmb=1.86.10.1457441532; __utmc=1; __utmz=1.1457441532.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
}


class Spider:

    # initialize the web url
    # initial url = http://top.qidian.com/Book/TopDetail.aspx?
    def __init__(self):
        self.siteURL = 'http://top.qidian.com/Book/TopDetail.aspx?'

    def getPage(self, topType, category, pageIndex):
        url = self.siteURL + 'TopType=' + str(topType) + '&Category=' + str(category) + '&PageIndex=' + str(pageIndex)
        data = requests.get(url, headers=headers)
        if data.status_code == 200:
            soup = BeautifulSoup(data.text, 'lxml')
            return soup
        else:
            print('Error 404 in getting page:' % url)
            return False

    def getContents(self, topType, category, pageIndex):
        soup = self.getPage(topType, category, pageIndex)
        if soup != False:
            ranks = soup.select('tr > td:nth-of-type(1)') # From the second data
            names = soup.select('a.name')
            cates = soup.select('a.type')
            votes = soup.select('tr > td:nth-of-type(4)')  # From the second data
            authors = soup.select('a.author')
    #        print(names)
            contents = []

            for rank, name, cate, vote, author in zip(ranks[1:], names, cates, votes[1:], authors):
                novelRank = rank.get_text()
                novelRank = novelRank.replace('\r', '').replace('\n', '').replace(' ', '').replace('\t', '')
                novelPage = name.get('href')
                novelName = name.get_text()
                novelName = novelName.replace('\r', '').replace('\n', '').replace(' ', '').replace('\t', '')
                novelCate = cate.get_text()
                novelVote = vote.get_text()
                novelVote = novelVote.replace('\r', '').replace('\n', '').replace(' ', '').replace('\t', '')
                authorName = author.get_text()
                authorName = authorName.replace('\r', '').replace('\n', '').replace(' ', '').replace('\t', '')
                authorPage = author.get('href')

                contents.append([novelRank, novelName, novelPage, novelCate, novelVote, authorName, authorPage])

            return contents
        else:
            return False

    def getDetailPage(self, infoURL):
        data = requests.get(infoURL, headers=headers)
        if data.status_code == 200:
            soup = BeautifulSoup(data.text, 'lxml')
            return soup
        else:
            print('Error 404 in getting page:' % infoURL)
            return False

    def getBrief(self, detailPage):
        data = detailPage.select('span[itemprop="description"]')
        brief = data[0].get_text()
        return brief

    def getDetailInfo(self, detailPage):
        totalClick = detailPage.select('td > span[itemprop="totalClick"]')
        monthlyClick = detailPage.select('td > span[itemprop="monthlyClick"]')
        weeklyClick = detailPage.select('td > span[itemprop="weeklyClick"]')
        totalRecommend = detailPage.select('td > span[itemprop="totalRecommend"]')
        monthlyRecommend = detailPage.select('td > span[itemprop="monthlyRecommend"]')
        weeklyRecommend = detailPage.select('td > span[itemprop="weeklyRecommend"]')
        wordCount = detailPage.select('td > span[itemprop="wordCount"]')
        wordMonthly = detailPage.select('div.yesterday_update > div.graph > div')

        info = []

        for tc, mc, wc, tr, mr, wr, wc, wm in zip(totalClick, monthlyClick, weeklyClick, totalRecommend, monthlyRecommend, weeklyRecommend, wordCount, wordMonthly):
            info.append([tc.get_text(), mc.get_text(), wc.get_text(), tr.get_text(), mr.get_text(), wr.get_text(), wc.get_text(), wm.get_text().replace('\r', '').replace('\n', '').replace(' ', '').replace('\t', '')])
        return info

    # ------------------------------------------
    # file operation

    def mkbasedir(self, topType):
        dict = {
            '3': '月票榜',
            '2': '推荐榜',
            '1': '点击榜'
        }
        baseName = dict.get(str(topType))
        path = baseName.strip()
        isExist = os.path.exists(path)
        if not isExist:
            print('创建文件夹 %s' % baseName)
            os.makedirs(path)
            return baseName
        else:
            print('文件夹 %s 已经创建' % baseName)
            return baseName

    def mkdir(self, basePath, category):
        dict = {
            '-1': '全部分类',
            '1': '奇幻玄幻',
            '2': '武侠仙侠',
            '3': '都市职业',
            '4': '历史军事',
            '5': '游戏竞技',
            '6': '科幻灵异',
            '7': '当月新书'
        }
        path = dict.get(str(category))
        totalPath = basePath + '/' + path
        path = path.strip()
        isExist = os.path.exists(totalPath)
        if not isExist:
            print('在 %s' % basePath, '下创建文件夹 %s' % path)
            os.makedirs(totalPath)
            return totalPath
        else:
            print('在 %s' % basePath, '下已有文件夹 %s' % path)
            return totalPath

    def savePageInfo(self, topType, category, pageIndex):
        contents = self.getContents(topType, category, pageIndex)
        if contents != False:
            basePath = self.mkbasedir(topType)
            totalPath = self.mkdir(basePath, category)
            fileName = totalPath + '/' + '排行榜.txt'
            with open(fileName, 'a+') as f:
                for item in contents:
                    rank = item[0]
                    novelName = item[1]
                    novelCate = item[3]
                    novelVote = item[4]
                    novelAuthor = item[5]
                    info = rank + ' ' + novelName + ' ' + novelCate + ' ' + novelCate + ' ' + novelAuthor + ' ' + novelVote + '\n'
                    f.write(info)
                print('已完成此页的数据读取')
    def savePagesInfo(self, topType, cateStart, cateEnd, pageStart, pageEnd):
        for category in range(cateStart, cateEnd + 1):
            if category == 0:
                category = -1
            for pageIndex in range(pageStart, pageEnd + 1):
                self.savePageInfo(topType, category, pageIndex)
        print('完毕')




spider = Spider()
spider.savePagesInfo(3, 0, 7, 1, 10)
# s = spider.getDetailPage('http://www.qidian.com/Book/3676417.aspx')
# spider.getDetailInfo(s)
# base = spider.mkbasedir(3)
# spider.mkdir(base, 1)


