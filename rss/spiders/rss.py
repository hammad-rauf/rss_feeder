from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup
import requests
import feedparser
import csv
import re
import os
from json import loads,load,dumps,dump
from datetime import datetime


class RssSpider(Spider):

    name = "rss"    

    start_urls = ['http://165.232.96.32/get?url=https://www.bbc.com/news']

    def __init__(self,*args, **kwargs):
        
        ## declearing variables
        self.data = []   
        self.database = []       
        self.currentdatabase = []      

        ## reading links.txt for rss links 

        filee = open('links.txt','r')
        data_list = filee.readlines()
        for temp in data_list:
            self.data.append(temp)
        filee.close()


        ## reading results.txt to save unique links
        filee = open("results.txt",'r')
        data_list = filee.readlines()
        for temp in data_list:
            self.database.append(temp.replace('\n',''))
        filee.close()

        ## clearing any data inside nodata.txt so that we can get new error log
        filee = open("nodata.txt",'w')
        filee.close()

        fields = ['description','image_url','published_at','source','title','updated_at','url']
        ## if data.csv is not in path we can create new file
        if not os.path.exists("data.csv"):

            with open("data.csv",'w',newline='',encoding='utf-8') as csv_file:
                file  =  csv.DictWriter(csv_file,fieldnames=fields)
                file.writeheader()
        else:
            with open("data.csv",'r',encoding='utf-8') as csv_file:
                file  =  csv.DictReader(csv_file)               
                count = len(list(file))
            if  count > 5:
                date = datetime.today().strftime('%Y-%m-%d-%X')
                date = date.replace(':','-')
                os.rename(r'data.csv',f'{date}.csv')
                with open("data.csv",'w',newline='',encoding='utf-8') as csv_file:
                    file  =  csv.DictWriter(csv_file,fieldnames=fields)
                    file.writeheader()


    def parse(self,response):

        for link in self.data:

            ## sendig data in feedparser
            data = feedparser.parse(link)
            
            flag = True

            for temp in data.entries:
                flag= False
                if temp['link'].count("https") > 1:
                    temp['link'] = f"https{temp['link'].split('https')[2]}"
                ## checking if link is not in database or already scraped in this current session 
                if not temp['link'] in self.database:
                    if not temp['link'] in self.currentdatabase:
                        filee = open("results.txt",'a')
                        filee.writelines(f"{temp['link']}\n")
                        filee.close()
                        self.currentdatabase.append(temp['link'])

                        ## sending api request
                        yield Request(f"http://165.232.96.32/get?url={temp['link']}",
                        callback=self.json_data)

            if flag:
                r = requests.get(link)
                soup = BeautifulSoup(r.content, features='xml')
                articles = soup.findAll('item')        
                for a in articles:
                    article_link = a.find('link').text
                    filee = open("results.txt",'a')
                    filee.writelines(f"{article_link}\n")
                    filee.close()
                    self.currentdatabase.append(article_link)
                    ## sending api request
                    yield Request(f"http://165.232.96.32/get?url={article_link}",
                    callback=self.json_data)
                    flag= False
                
                if flag:
                    ## if no links are returned from feedparser i will save that link in nodata.txt
                    filee = open("nodata.txt",'a')
                    filee.writelines(f"No data from link: {link}\n")
                    filee.close()

                        

    def json_data(self,response):
        
        ## reading api results
        data = loads(response.text)

        with open("data.csv",'a',newline='',encoding='utf-8') as csv_file:

            ## saving api data for csv
            try:
                description = data['description']
                description = description.replace('\n','')
            except:
                description = None
            
            try:
                image_url = data['image_url']
            except:
                image_url = None
                
            try:
                published_at = data['published_at']
            except: 
                published_at = None

            try:
                source = data['source']
            except:
                source = None
            
            try:
                title = data['title']
            except:
                title = None


            try:
                updated_at = data['updated_at']
            except:
                updated_at = None

            
            try:
                url = data['url']
            except:
                url =  None

            #description,image_url,published_at,source,title,updated_at,url
            fields = ['description','image_url','published_at','source','title','updated_at','url']
            file  =  csv.DictWriter(csv_file,fieldnames=fields)

            ## adding row in csv file
            file.writerow({
                'description':description,
                'image_url':image_url,
                'published_at':published_at,
                'source':source,
                'title':title,
                'updated_at':updated_at,
                'url':url
            })
            yield {
                'description':description,
                'image_url':image_url,
                'published_at':published_at,
                'source':source,
                'title':title,
                'updated_at':updated_at,
                'url':url
            }
