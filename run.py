from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import sys
    
process = CrawlerProcess({'SPIDER_MODULES': 'rss.spiders'})
process.crawl('rss')
process.start()
