import argparse
import time
import os

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#Args - Unsanitized (did i say it is not supposed to be robust ?)
def getArgs(webStruct):
    parser = argparse.ArgumentParser(description='Shitty web crawler for TutorialPoints.')
    parser.add_argument('url',
                        help='Url of a page from the tutorial')
    args = parser.parse_args()
    ua = UserAgent()

    #Get url and headers for project
    webStruct['url'] = args.url
    webStruct['headers'] = {'User-Agent': ua.chrome}

#First Get request to list page to crawl
def initCrawl(webStruct, projectStruct):
    #Initial Get : Request+soup shenanigans
    r = requests.get(webStruct['url'], headers=webStruct['headers'])
    soup = BeautifulSoup(r.text, "html.parser")
    firstPage = soup.find('ul', {'class': 'nav nav-list primary left-menu'})

    #Get Chapters list and tutorial title
    projectStruct['chapterList'] = firstPage.findChildren('a')[1:]
    projectStruct['title'] = firstPage.find("li", {'class':'heading'}).text

#Define and load html tag parsers in a dictionary
def parseTable(elem):
    mTable = ""
    for line in elem.findChildren(): 
        mLines = ""
        for tab in line.findChildren():
            mLines += tab.text + " "
        if mLines != "":
            mTable += mLines + "\n"
    return mTable

def parseAsText(elem):
    return elem.text + "\n"

def initParserDict(projectStruct):
    legalTags = ["h1","h2","p","pre","table"]
    for tag in legalTags:
        if(tag != "table"):
            projectStruct['dictParser'][tag] = parseAsText

    projectStruct['dictParser']["table"] = parseTable
    projectStruct['legalTags'] =  legalTags

#Assumes Script owner as folder creation right
def initBoilerPlate(webStruct, projectStruct):
    projectStruct['path'] = "./" + projectStruct['title'] + "/"
    #init local folder
    if not os.path.exists(projectStruct['path']):
        os.makedirs(projectStruct['path'])

    #init local cache
    if not os.path.exists(projectStruct['path'] + ".cache"):
        os.makedirs(projectStruct['path'] + ".cache") 
    
#Get main body from the page

def encodeUrl(cUrl):
    cUrl = cUrl.replace("/", "%2F")
    cUrl = cUrl.replace(":", "%3A")
    return cUrl

def isInCache(cUrl, path):
    return os.path.exists(path + ".cache/" + encodeUrl(cUrl))

def fetchFromFile(cUrl, path):
    htmlText = ""
    with open( path + ".cache/" + encodeUrl(cUrl), "r") as text_file:
        htmlText = text_file.read()
    return htmlText

def saveInCache(cUrl, path, htmlText):
    with open( path + ".cache/" + encodeUrl(cUrl), "w") as text_file:
        text_file.write("%s" % htmlText.encode("utf8"))

def getChapter(href, headers, path):
    cUrl = "https://www.tutorialspoint.com/" + href

    if(isInCache(cUrl, path)):
        textPage = fetchFromFile(cUrl, path)
    else:
        time.sleep(1)
        r = requests.get(cUrl, headers=headers)
        textPage = r.text
        saveInCache(cUrl, path, textPage)
    soup = BeautifulSoup(textPage, "html.parser")
    htmlChapter = soup.find('div', {'class': 'col-md-7 middle-col'})
    return htmlChapter

#Turn main body into something (text for now)
def parseChapter(htmlChapter, legalTags, dictParser):
    currentPage = ""
    cTitle = htmlChapter.find("h1").text
    print(cTitle)

    #Loop through main tab to get chapter
    for child in htmlChapter.findChildren():
        if(legalTags.__contains__(child.name)):
            currentPage += dictParser[child.name](child)
    
    #Insert current page in Dict
    projectStruct['tutorial'].append((cTitle, currentPage))

def dumpTutorial(webStruct, projectStruct):
    for chapter in projectStruct['chapterList']:
        htmlChapter = getChapter(chapter['href'], webStruct['headers'], projectStruct['path'])
        parseChapter(htmlChapter, projectStruct['legalTags'], projectStruct['dictParser'])

#Broken if no folder
def writeToFile(path, cTitle, chapter, idx):
    with open( path + str(idx) + " - " + cTitle + ".txt", "w") as text_file:
        text_file.write("%s" % chapter.encode("utf8"))

def saveToFolder(projectStruct):
    for idx, chapter in enumerate(projectStruct['tutorial']):
        cTitle = chapter[0]
        text = chapter[1]
        if(cTitle.find("/") != -1):
            cTitle = cTitle.replace("/", "")
        writeToFile(projectStruct['path'], cTitle, text, idx)


def init(webStruct, projectStruct):
    getArgs(webStruct)
    initCrawl(webStruct, projectStruct)
    initParserDict(projectStruct)
    initBoilerPlate(webStruct, projectStruct)

def main(webStruct, projectStruct):
    dumpTutorial(webStruct, projectStruct)
    saveToFolder(projectStruct)

webStruct = {'url' : "",
                'headers' : {}}

projectStruct = {   'title' : "",
                    'path' : "",
                    'dictParser' : {},
                    'chapterList' : [],
                    'tutorial' : [],
                    'legalTags' : []
                }

init(webStruct, projectStruct)
main(webStruct, projectStruct)

#https://www.tutorialspoint.com/lisp/lisp_overview.htm