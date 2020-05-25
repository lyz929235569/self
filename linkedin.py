import requests
from lxml import etree
import re
import copy
import json

LINKS_FINISHED=[]  #已抓取的linkedin用户
maxpage =50  #百度前50页

def crawl(url,s):
    try:
        url = get_linkedin_url(url, copy.deepcopy(s)).replace('cn.linkedin.com', 'www.linkedin.com')  # 百度搜索出的结果是百度跳转链接，要提取出linkedin的链接。
        if len(url) > 0 and url not in LINKS_FINISHED:
            if "https" not in url:
                url = url.replace("http","https")
            LINKS_FINISHED.append(url)
            failure = 0
            while failure < 10:
                try:
                    print(url)
                    r = s.get(url, timeout=10)
                except Exception as e:
                    failure += 1
                    continue
                if r.status_code == 200:
                    # r.encoding="utf-8"

                    parse(r.content, url)
                    break
                else:
                    print('%s %s' % (r.status_code, url))
                    failure += 2
            if failure >= 10:
                print('Failed: %s' % url)
    except Exception as e:
        pass


def parse(content,url):
    """ 解析一个员工的Linkedin主页 """
    content = content.replace('&quot;', '"')
    tree = etree.HTML(content)
    code_list = tree.xpath("//code")

    for code in code_list:
        try:
            data = code.xpath("./text()")[0]
            data_dict = json.loads(data)

            if data_dict.get("data", {}).get("firstName"):
                name = data_dict.get("data", {}).get("lastName") + data_dict.get("data", {}).get("firstName")
                occupation = data_dict.get("data", {}).get("occupation")

                print('姓名: %s'  %(name),'身份/职位: %s' % occupation)

                locationName = re.findall('"locationName":"(.*?)"', data)[-1]
                if locationName:
                    print('位置: %s' % locationName)
                connectionsCount = re.findall('"connectionsCount":(\d+)', data)
                if connectionsCount:
                    print('好友人数: %s' % connectionsCount)

            educations = re.findall('(\{[^\{]*?profile\.Education"[^\}]*?\})', content)
            if educations:
                print
                '教育经历:'
            for edu in educations:
                schoolName = re.findall('"schoolName":"(.*?)"', edu)
                fieldOfStudy = re.findall('"fieldOfStudy":"(.*?)"', edu)
                degreeName = re.findall('"degreeName":"(.*?)"', edu)
                timePeriod = re.findall('"timePeriod":"(.*?)"', edu)
                schoolTime = ''
                if timePeriod:
                    startdate_txt = ' '.join(re.findall(
                        '(\{[^\{]*?"\$id":"%s,startDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                        content))
                    enddate_txt = ' '.join(re.findall(
                        '(\{[^\{]*?"\$id":"%s,endDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                        content))
                    start_year = re.findall('"year":(\d+)', startdate_txt)
                    start_month = re.findall('"month":(\d+)', startdate_txt)
                    end_year = re.findall('"year":(\d+)', enddate_txt)
                    end_month = re.findall('"month":(\d+)', enddate_txt)
                    startdate = ''
                    if start_year:
                        startdate += '%s' % start_year[0]
                        if start_month:
                            startdate += '.%s' % start_month[0]
                    enddate = ''
                    if end_year:
                        enddate += '%s' % end_year[0]
                        if end_month:
                            enddate += '.%s' % end_month[0]
                    if len(startdate) > 0 and len(enddate) == 0:
                        enddate = '现在'
                    schoolTime += '   %s ~ %s' % (startdate, enddate)
                    if schoolName:
                        fieldOfStudy = '   %s' % fieldOfStudy[0] if fieldOfStudy else ''
                        degreeName = '   %s' % degreeName[0] if degreeName else ''
                        print('%s %s %s %s' % (schoolName[0], schoolTime, fieldOfStudy, degreeName))

            position = re.findall('(\{[^\{]*?profile\.Position"[^\}]*?\})', content)
            if position:
                print('工作经历:')
            for pos in position:
                companyName = re.findall('"companyName":"(.*?)"', pos)
                title = re.findall('"title":"(.*?)"', pos)
                locationName = re.findall('"locationName":"(.*?)"', pos)
            timePeriod = re.findall('"timePeriod":"(.*?)"', pos)
            positionTime = ''
            if timePeriod:
                startdate_txt = ' '.join(re.findall(
                    '(\{[^\{]*?"\$id":"%s,startDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                    content))
                enddate_txt = ' '.join(re.findall(
                    '(\{[^\{]*?"\$id":"%s,endDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                    content))
                start_year = re.findall('"year":(\d+)', startdate_txt)
                start_month = re.findall('"month":(\d+)', startdate_txt)
                end_year = re.findall('"year":(\d+)', enddate_txt)
                end_month = re.findall('"month":(\d+)', enddate_txt)
                startdate = ''
                if start_year:
                    startdate += '%s' % start_year[0]
                    if start_month:
                        startdate += '.%s' % start_month[0]
                enddate = ''
                if end_year:
                    enddate += '%s' % end_year[0]
                    if end_month:
                        enddate += '.%s' % end_month[0]
                if len(startdate) > 0 and len(enddate) == 0:
                    enddate = '现在'
                positionTime += ('   %s ~ %s' % (startdate, enddate))

            publication = re.findall('(\{[^\{]*?profile\.Publication"[^\}]*?\})', content)
            if publication:
                print
                '出版作品:'
            for one in publication:
                name = re.findall('"name":"(.*?)"', one)
                publisher = re.findall('"publisher":"(.*?)"', one)
                if name:
                    print('    %s %s' % (name[0], '   出版社: %s' % publisher[0] if publisher else ''))

            honor = re.findall('(\{[^\{]*?profile\.Honor"[^\}]*?\})', content)
            if honor:
                print
                '荣誉奖项:'
            for one in honor:
                title = re.findall('"title":"(.*?)"', one)
                issuer = re.findall('"issuer":"(.*?)"', one)
                issueDate = re.findall('"issueDate":"(.*?)"', one)
                issueTime = ''
                if issueDate:
                    issueDate_txt = ' '.join(
                        re.findall('(\{[^\{]*?"\$id":"%s"[^\}]*?\})' % issueDate[0].replace('(', '\(').replace(')', '\)'),
                                   content))
                    year = re.findall('"year":(\d+)', issueDate_txt)
                    month = re.findall('"month":(\d+)', issueDate_txt)
                    if year:
                        issueTime += '   发行时间: %s' % year[0]
                        if month:
                            issueTime += '.%s' % month[0]
                if title:
                    print('    %s %s %s' % (title[0], '   发行人: %s' % issuer[0] if issuer else '', issueTime))


                    organization = re.findall('(\{[^\{]*?profile\.Organization"[^\}]*?\})', content)
                    if organization:
                        print('参与组织:')

                    for one in organization:
                        name = re.findall('"name":"(.*?)"', one)
                        timePeriod = re.findall('"timePeriod":"(.*?)"', one)
                        organizationTime = ''
                        if timePeriod:
                            startdate_txt = ' '.join(re.findall(
                                '(\{[^\{]*?"\$id":"%s,startDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                                content))
                            enddate_txt = ' '.join(re.findall(
                                '(\{[^\{]*?"\$id":"%s,endDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                                content))
                            start_year = re.findall('"year":(\d+)', startdate_txt)
                            start_month = re.findall('"month":(\d+)', startdate_txt)
                            end_year = re.findall('"year":(\d+)', enddate_txt)
                            end_month = re.findall('"month":(\d+)', enddate_txt)
                            startdate = ''
                            if start_year:
                                startdate += '%s' % start_year[0]
                                if start_month:
                                    startdate += '.%s' % start_month[0]
                            enddate = ''
                            if end_year:
                                enddate += '%s' % end_year[0]
                                if end_month:
                                    enddate += '.%s' % end_month[0]
                            if len(startdate) > 0 and len(enddate) == 0:
                                enddate = '现在'
                            organizationTime += '   %s ~ %s' % (startdate, enddate)
                        if name:
                            print('    %s %s' % (name[0], organizationTime))


                    patent = re.findall('(\{[^\{]*?profile\.Patent"[^\}]*?\})', content)
                    if patent:
                        print('专利发明:')

                    for one in patent:
                        title = re.findall('"title":"(.*?)"', one)
                        issuer = re.findall('"issuer":"(.*?)"', one)
                        url = re.findall('"url":"(http.*?)"', one)
                        number = re.findall('"number":"(.*?)"', one)
                        localizedIssuerCountryName = re.findall('"localizedIssuerCountryName":"(.*?)"', one)
                        issueDate = re.findall('"issueDate":"(.*?)"', one)
                        patentTime = ''
                        if issueDate:
                            issueDate_txt = ' '.join(
                                re.findall('(\{[^\{]*?"\$id":"%s"[^\}]*?\})' % issueDate[0].replace('(', '\(').replace(')', '\)'),
                                           content))
                            year = re.findall('"year":(\d+)', issueDate_txt)
                            month = re.findall('"month":(\d+)', issueDate_txt)
                            day = re.findall('"day":(\d+)', issueDate_txt)
                            if year:
                                patentTime += '   发行时间: %s' % year[0]
                                if month:
                                    patentTime += '.%s' % month[0]
                                    if day:
                                        patentTime += '.%s' % day[0]
                        if title:
                            print('    %s %s %s %s %s %s' % (
                            title[0], '   发行者: %s' % issuer[0] if issuer else '', '   专利号: %s' % number[0] if number else '',
                            '   所在国家: %s' % localizedIssuerCountryName[0] if localizedIssuerCountryName else '', patentTime,
                            '   专利详情页: %s' % url[0] if url else ''))


            project = re.findall('(\{[^\{]*?profile\.Project"[^\}]*?\})', content)
            if project:
                print('所做项目:')

            for one in project:
                title = re.findall('"title":"(.*?)"', one)
                description = re.findall('"description":"(.*?)"', one)
                timePeriod = re.findall('"timePeriod":"(.*?)"', one)
                projectTime = ''
                if timePeriod:
                    startdate_txt = ' '.join(re.findall(
                        '(\{[^\{]*?"\$id":"%s,startDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                        content))
                    enddate_txt = ' '.join(re.findall(
                        '(\{[^\{]*?"\$id":"%s,endDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                        content))
                    start_year = re.findall('"year":(\d+)', startdate_txt)
                    start_month = re.findall('"month":(\d+)', startdate_txt)
                    end_year = re.findall('"year":(\d+)', enddate_txt)
                    end_month = re.findall('"month":(\d+)', enddate_txt)
                    startdate = ''
                    if start_year:
                        startdate += '%s' % start_year[0]
                        if start_month:
                            startdate += '.%s' % start_month[0]
                    enddate = ''
                    if end_year:
                        enddate += '%s' % end_year[0]
                        if end_month:
                            enddate += '.%s' % end_month[0]
                    if len(startdate) > 0 and len(enddate) == 0:
                        enddate = '现在'
                    projectTime += '   时间: %s ~ %s' % (startdate, enddate)
                if title:
                    print('    %s %s %s' % (title[0], projectTime, '   项目描述: %s' % description[0] if description else ''))


            volunteer = re.findall('(\{[^\{]*?profile\.VolunteerExperience"[^\}]*?\})', content)
            if volunteer:
                print
                '志愿者经历:'
            for one in volunteer:
                companyName = re.findall('"companyName":"(.*?)"', one)
                role = re.findall('"role":"(.*?)"', one)
                timePeriod = re.findall('"timePeriod":"(.*?)"', one)
                volunteerTime = ''
                if timePeriod:
                    startdate_txt = ' '.join(re.findall(
                        '(\{[^\{]*?"\$id":"%s,startDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                        content))
                    enddate_txt = ' '.join(re.findall(
                        '(\{[^\{]*?"\$id":"%s,endDate"[^\}]*?\})' % timePeriod[0].replace('(', '\(').replace(')', '\)'),
                        content))
                    start_year = re.findall('"year":(\d+)', startdate_txt)
                    start_month = re.findall('"month":(\d+)', startdate_txt)
                    end_year = re.findall('"year":(\d+)', enddate_txt)
                    end_month = re.findall('"month":(\d+)', enddate_txt)
                    startdate = ''
                    if start_year:
                        startdate += '%s' % start_year[0]
                        if start_month:
                            startdate += '.%s' % start_month[0]
                    enddate = ''
                    if end_year:
                        enddate += '%s' % end_year[0]
                        if end_month:
                            enddate += '.%s' % end_month[0]
                    if len(startdate) > 0 and len(enddate) == 0:
                        enddate = '现在'
                    volunteerTime += '   时间: %s ~ %s' % (startdate, enddate)
                if companyName:
                    print('%s %s %s' % (companyName[0], volunteerTime, '   角色: %s' % role[0] if role else ''))




def get_linkedin_url(url,s):
    """ 百度搜索出来的是百度跳转链接，要从中提取出linkedin链接 """
    try:
        r = s.get(url, allow_redirects=False)
        if r.status_code == 302 and 'Location' in r.headers.keys() and 'linkedin.com/in/' in r.headers['Location']:
            return r.headers['Location']
    except Exception as e:
        print('get linkedin url failed: %s' % url)
    return

def login(laccount,lpassword):
    """ 根据账号密码登录linkedin """
    s = requests.Session()
    r = s.get('https://www.linkedin.com/uas/login',headers={"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Mobile Safari/537.36"})
    # print(r.content)
    r.encoding="utf-8"
    tree = etree.HTML(r.text)
    # print(r.text)
    ac = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]/form/input[2]/@value'))

    sIdString = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[3]/@value'))

    csrfToken = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[1]/@value'))

    parentPageKey = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[4]/@value'))
    trk = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[6]/@value'))
    authUUID = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[7]/@value'))
    session_redirect = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[8]/@value'))
    fp_data = ''.join(tree.xpath('//*[@id="fp_data_login"]/@value'))
    _d = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[11]/@value'))
    showGoogleOneTapLogin = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[12]/@value'))
    controlId = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[13]/@value'))
    pageInstance = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[5]/@value'))
    loginCsrfParam = ''.join(tree.xpath('//*[@id="app__container"]/main/div[2]//input[9]/@value'))
    payload = {
        'csrfToken': csrfToken,
        'session_key': laccount,
        "ac":ac,
        'sIdString': sIdString,
        'parentPageKey': parentPageKey,
        'pageInstance': pageInstance,
        'trk': trk,
        'authUUID': authUUID,
        'session_redirect': session_redirect,
        'loginCsrfParam': loginCsrfParam,
        'fp_data': fp_data,
        '_d': _d,
        "showGoogleOneTapLogin":showGoogleOneTapLogin,
        "controlId":controlId,
        'session_password': lpassword,
    }
    s.post('https://www.linkedin.com/checkpoint/lg/login-submit', data=payload)

    return s

if __name__ == '__main__':
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36","Cookie":"BAIDUID=D6627C70BE57D4856C07BF07E335EB90:FG=1; BIDUPSID=D6627C70BE57D4856C07BF07E335EB90; PSTM=1567411385; BD_UPN=12314753; MCITY=-%3A; yjs_js_security_passport=ab24f4ad0ee7977f66049c06c489eb034001f9f8_1590200709_js; BDSFRCVID=bLIOJeC62uACKfru1BE1Kwh9ZMVxVmJTH6aI8ANlAOYulDJRfvI-EG0Pjf8g0Ku-F1NKogKK0mOTHv8F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tR4eVC-htCD3fP36q4vEh4P8bMrXetJyaR3a2pTvWJ5TMCoGLfbvbRD0Dt54Jxnf2n5z2xQyQJ6kShPC-fuWLfCjLtnk-47RWHrhLqIE3l02VbcIe-t2ynQDQGQwB-RMW20jWl7mWPLWsxA45J7cM4IseboJLfT-0bc4KKJxbnLWeIJEjj6jK4JKDNuqq6bP; H_PS_PSSID=31360_1426_31325_21113_31111_31464_30823; H_PS_645EC=01d9o0YqTC8Oru7sccQRnrlnKakJWDyy2OsmwruA5SNe9qeHck14X2CFFgI; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598"}
    company_name=input("xxx")

    url = 'https://www.baidu.com/s?ie=UTF-8&wd=%20%7C%20领英%20' + company_name + '%20site%3Alinkedin.com'
    print(url)

    results = []
    failure = 0
    while len(url) > 0 and failure < 10:
        try:
            r = requests.get(url,headers=headers)
        except Exception as e:
            failure += 1
            continue
        if r.status_code == 200:

            r.encoding="utf-8"
            print(r.text)
            hrefs = list(set(re.findall('("http://www\.baidu\.com/link\?url=.*?")', r.text)))
            print(hrefs)
            # print(hrefs[0])
            for href in hrefs[0:1]:
                # print(href)
                crawl(href.replace('"',""), copy.deepcopy(s))

            results += hrefs
            tree = etree.HTML(r.content)
            nextpage_txt = tree.xpath(
                '//div[@id="page"]/a[@class="n" and contains(text(), "下一页")]/@href'.decode('utf8'))
            url = 'http://www.baidu.com' + nextpage_txt[0].strip() if nextpage_txt else ''
            failure = 0
            maxpage -= 1
            if maxpage <= 0:
                break
            else:
                failure += 2
                print( 'search failed: %s' % r.status_code)

            if failure >= 10:
                print('search failed: %s' % url)


