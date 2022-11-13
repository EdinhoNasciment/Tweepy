from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from wordcloud import WordCloud, STOPWORDS
from selenium.webdriver import Firefox
from bs4 import BeautifulSoup as Soup
from pathlib import Path
from time import sleep
import platform
import nltk
import re

PATH_GECKODRIVER_WINDOWS = Path("tweepy/webdriver/geckodriver_windows.bin").absolute()
PATH_GECKODRIVER_LINUX   = Path("tweepy/webdriver/geckodriver_linux.bin").absolute()
PATH_PNG_OUTPUT          = Path("tweepy/img/cloud.png").absolute()
FETCH_TWEETS             = 50 

print(PATH_GECKODRIVER_LINUX)
print(PATH_GECKODRIVER_WINDOWS)
print(PATH_PNG_OUTPUT)

nltk.download('stopwords')

service = None
if(platform.system() == "Windows"):
    service = Service(PATH_GECKODRIVER_WINDOWS)
else:
    service = Service(PATH_GECKODRIVER_LINUX)

FIREFOX_OPTIONS = Options()
FIREFOX_OPTIONS.headless = True
driver = Firefox(service=service, options=FIREFOX_OPTIONS)
driver.set_window_size(1920, 1080)

def wait_element(tag, text):
    for _ in text:
        html_parser = Soup(driver.page_source, "html.parser")
        element = html_parser.find(tag, string=text)
        print(element)
        if(element != None):
            return False

    return True

def gen_twittes_txt(max_post):
    raw_html_map = {}
    size_mapper = {}
    search = True
    i = 1

    while(search == True and max_post > len(raw_html_map)):
        soup = Soup(driver.page_source, "html.parser")
        for tweet in soup.find_all("article"):
            for article in tweet.find_all(attrs={"data-testid" : "tweetText"}):
                full_txt = ""
                for txt in article.find_all("span"):
                    if(txt != None):
                        full_txt += re.sub("<span.*?>|</span>|<.*?>", "", str(txt))
                raw_html_map[full_txt] = None

        driver.execute_script(f"window.scrollTo(0, window.innerHeight*{i});")

        try:
            size_mapper[len(raw_html_map)] = size_mapper[len(raw_html_map)] + 1
        except KeyError: 
            size_mapper[len(raw_html_map)] = 1

        if(size_mapper[len(raw_html_map)] > 4):
            search = False

        i += 1
        print(size_mapper)
        sleep(1)

    return list(raw_html_map.keys())

def wait_load():
    wait_load = True
    while(wait_load):
        wait_load = wait_element("span", ["What’s happening"])
        sleep(1)

def gen_stopwords():
    stopwords = nltk.corpus.stopwords.words('portuguese')
    for word in "to;dia;hoje;lá;pra;vai;todo;vc;&amp;q;todo;i;amp;hj;n;utm_medium;p;tá;www1;ta;pq;http;https;Bom dia;tô;mano;D;então;X;Alguém;dá;fez;b".split(";"):
        stopwords.append(word)
    return stopwords

def get_tweets_words(stopword):
    tweets = gen_twittes_txt(FETCH_TWEETS)
    driver.close()

    all_txt = ""
    tweets_words = {}

    for t in tweets:
        print("="*len(t))
        print(t)
        print("="*len(t))

        all_txt += t

        for w in t.split(" "):
            word = w.lstrip().rstrip()
            for stop in stopword:
                if(stop != word and word != ""):
                    try:
                        tweets_words[word][t] = None
                    except KeyError:
                        tweets_words[word] = { t : None }

    return all_txt, tweets_words

def gen_cloud_word(stopword, txt):
    cloud = WordCloud(
        background_color="white"
    ,   stopwords=stopword
    ,   height=600
    ,   width=400
    ).generate(txt)

    cloud.to_file(PATH_PNG_OUTPUT)

def main(latitude, longitude, raio, palavra_chave):
    args = {
        "latitude"  : latitude
    ,   "longitude" : longitude
    ,   "raio"      : raio
    }
    url = f"https://twitter.com/search?q=geocode:{args['latitude']},{args['longitude']},{args['raio']}km {palavra_chave}&src=typed_query&f=live&lang=en-us"
    driver.get(url)

    wait_load()

    stopword = gen_stopwords()

    all_txt, tweets_words = get_tweets_words(stopword)

    gen_cloud_word(stopword, all_txt)

main( -21.789341037025892, -48.17630560469828, 5, "")