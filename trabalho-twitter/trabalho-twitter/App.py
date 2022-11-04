from pathlib import Path
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup as Soup
from time import sleep
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import re
import nltk

service = Service("./geckodriver")
driver = Firefox(service=service)

def wait_element(tag, text):
    for t in text:
        html_parser = Soup(driver.page_source, "html.parser")
        element = html_parser.find("span", string=text)
        print(element)
        if(element != None):
            return False

    return True

def gen_twittes_txt(max_post):
    raw_html_map = {}
    while(max_post > len(raw_html_map)):
        soup = Soup(driver.page_source, "html.parser")
        for tweet in soup.find_all("article"):
            for article in tweet.find_all(attrs={"data-testid" : "tweetText"}):
                full_txt = ""
                for txt in article.find_all("span"):
                    if(txt != None):
                        full_txt += re.sub("<span.*?>|</span>|<.*?>", "", str(txt))
                raw_html_map[full_txt] = None

        sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(len(raw_html_map))
        sleep(2)

    return list(raw_html_map.keys())

def wait_load():
    wait_load = True
    while(wait_load):
        wait_load = wait_element("span", ["What’s happening"])
        sleep(1)

def init_console():
    args = {
        "latitude"  : -21.789341037025892 
    ,   "longitude" : -48.17630560469828
    ,   "raio"      : 10
    }
    url = f"https://twitter.com/search?q=geocode:{args['latitude']},{args['longitude']},{args['raio']}km&src=typed_query&f=live&lang=en-us"
    driver.get(url)

    wait_load()

    all_txt = ""
    for t in gen_twittes_txt(500):
        all_txt += t

    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words('portuguese')

    cloud = WordCloud(
        background_color="white"
    ,   stopwords=stopwords
    ,   height=600
    ,   width=400
    )

    cloud.generate(all_txt)

    cloud.to_file("cloud.png")

init_console()