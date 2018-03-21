## Overview
Bamboo Listeners is a python based project utilizing scrapy to periodically ingest data collected from various websites. 
### Installation
Install using the supplied requirements.txt
    cd ~/project-folder
    pip install -r requirements.txt
### Usage

The Bamboo Listeners requires a mysql backend with tables constructed to consume results.  Visit each scrapy pipeline to edit, update, view required fields.

    crawl sbnation-articles -a domain=<domain-name>  (do not include www. or .com)
    crawl seattletimes-auth -a startdate=<YYYY-MM-DD> -a enddate=<YYYY-MM-DD> -a search=* -a perpage=200 -a username=<username> -a password=<password>
