import requests
import requests.auth
from bs4 import BeautifulSoup
import ConfigParser
import time
import timeit
import pandas
import numpy as np
from gluon.contrib.appconfig import AppConfig

class Rff:
    def __init__(self):
        self.credentials = {'username':'df','password':'df','clientid':'df','clientsecret':'df','useragent':'df'}
        self.headers = ''
        self.authHeaders = ''
        self.bearHeaders = ''
    #Load user credentials
    def loadScriptConfig(self):
        config = ConfigParser.ConfigParser()
        config.read('\r.ini')
        self.credentials['username'] = config.get('OAUTH','username')
        self.credentials['password'] = config.get('OAUTH','password')
        self.credentials['clientid'] = config.get('OAUTH','clientid')
        self.credentials['clientsecret'] = config.get('OAUTH','clientsecret')
        self.credentials['useragent'] = config.get('OAUTH','useragent')+'/'+config.get('OAUTH','useragentversion')+' by '+credentials['username']

    def loadAppConfig(self):
        myconf = AppConfig(reload=False)
        self.credentials['clientid'] = myconf.take('app.clientid')
        self.credentials['clientsecret'] = myconf.take('app.clientsecret')

    #Perform OAUTH fetch token
    def genHeaders(self):
        client_auth = requests.auth.HTTPBasicAuth(credentials['clientid'], credentials['clientsecret'])
        post_data = {"grant_type": "password", "username": credentials['username'], "password": credentials['password']}
        headers = {"User-Agent": credentials['useragent']}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        token = response.json()['access_token'].encode("UTF-8")
        authHeaders = {"Authorization": token, "User-Agent": credentials['useragent']}
        bearHeaders = {"Authorization": ("bearer "+token), "User-Agent": credentials['useragent']}

    def genHeaders(self,code,redirect):
        global headers,authHeaders,bearHeaders
        client_auth = requests.auth.HTTPBasicAuth(credentials['clientid'], credentials['clientsecret'])
        post_data = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data)
        token = response.json()['access_token'].encode("UTF-8")
        authHeaders = {"Authorization": token}
        bearHeaders = {"Authorization": ("bearer "+token)}

    #Get all subs
    #TODO handle users with listings on more than one page
    def getSubscriptions():
        response = requests.get("https://oauth.reddit.com/subreddits/mine/subscriber",headers=bearHeaders)
        subs = []
        for listing in response.json()['data']['children']:		
            print listing['data']['url']
            subs.append("https://www.reddit.com"+listing['data']['url'])
        print 'Found ' + str(len(subs)) + ' subreddits'
        return subs

    def getTrendingThreads(subreddit):
        response = requests.get(subreddit, headers=authHeaders)
        soup = BeautifulSoup(response.content,'html.parser')
        threads = []
        for link in soup.findAll('a'):
            if u'comment' in link.text:
                threads.append(link.get('href'))
        return threads

    def getComments(thread):
        comments = []
        try:
            response = requests.get(thread, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            sub = thread[thread.index('/r/'):]
            sub = sub[3:]
            sub = sub[:sub.index('/')]
            title = thread[thread[0:len(thread)-2].rfind('/')+1:-1]
            print 'Processing Subreddit: '+ sub + ' Thread: ' + title
        except:
            print 'Error Unable to process thread'
            return []
        for comment in soup.findAll("a", class_='author'):
            author = comment.text
            comments.append((author,sub,title))
        return comments

    def findFriends():
        startTime = time.time()
        loadScriptConfig()
        genHeaders()
        threads = []
        comments = []
        subs = getSubscriptions()
        print 'Retrieving comment threads...'
        for sub in subs:
            threads = threads + getTrendingThreads(sub)
        print 'All threads retrieved in ' + str(time.time() - startTime) + 's'
        for idx,thread in enumerate(threads):
            print ('('+str(idx)+'/'+str(len(threads))+')')
            comments = comments + getComments(thread)
        print 'Found ' + str(len(comments)) + ' in ' + str(len(threads)) + ' threads across ' + str(len(subs)) + ' subreddits'
        analyzeComments(comments)

    def analyzeComments(comments):
        df = pandas.DataFrame(comments,columns=['user','subreddit','title'])
        topMatches = df.groupby(['user']).subreddit.nunique('count').nlargest(10)	
        matchDetails = df.where(df.user.isin(topMatches.index)).groupby(['user','subreddit']).count()
        print topMatches
        print matchDetails


    def runTimedNoArg(methodName, method):
        print methodName + '()'
        startTime = time.time()
        method()
        print '-'+methodName + '() finished in ' + str(time.time() - startTime) + 's'

#runTimedNoArg('findFriends',findFriends)
