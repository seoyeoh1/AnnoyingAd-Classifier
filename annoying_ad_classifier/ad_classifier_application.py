import time

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sklearn.feature_extraction.text import CountVectorizer

model = joblib.load('/Users/SeoyeonHong/Desktop/annoying_ad_classifier/model/ad_classifier_rf.pkl')

# Retrieving Feature (Vectors) List for Classifier
with open("/Users/SeoyeonHong/Desktop/annoying_ad_classifier/model/features.txt") as sample:
    features = []
    for line in sample:
        features.append(line.rstrip())

# Setting CountVectorizer for new data
vec = CountVectorizer(encoding='utf-8', decode_error='strict', vocabulary=features)


# Accessing website
def open_url(url):
    """This function takes a website url, and returns the HTML source code using Selenium,
    and a list of all the divs in the source code using the get_div function"""
    driver.get(url)
    time.sleep(20)


# Preprocessing data
def strip_html_tags(text):
    """remove html tags from text"""
    soup = bs(text, "lxml")
    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def get_divs(code):
    """This function collects all the div tags from an HTML"""
    soup = bs(code)
    divs = soup.select("div")
    return divs


def refine_divs(divs):
    global refined_divs
    refined_divs = []
    j = 0
    k = 1
    for j in range(len(divs) - 1):
        elem = str(divs[j].get('id'))
        next_elem = str(divs[k].get('id'))
        if next_elem:
            if (elem in next_elem) or (next_elem in elem):
                k = k + 1
            else:
                refined_divs.append(divs[k])
                j = j + 1
                k = k + 1
        else:
            refined_divs.append(divs[k])
    refined_divs.append(divs[0])
    return refined_divs


# Retrieving ads from website (the div tags that contain ad tags)
def get_ads(divs):
    global ad_tags
    ad_tags = []
    ad_indicators = ["33across", "adnxs", "chitika", "districtm", "Adx", "doubleclick.net", "emx", "googlesyndication",
                     "google_ads_iframe_", "adsbygoogle", "googletagservices", "googleadservices", "infolinks",
                     "crwdcntrl.net", "medianet", "mgid", "MOAT", "onesignal", "openx", "piano", "tinypass",
                     "ads.pubmatic.com", "popads.net", "clksite.com/AdServe", "rubiconproject", "smartadserver",
                     "sovrn", "taboola”, triplelift", "verizonmedia", "beap.gemini.yahoo.com"]
    for div in divs[:]:
        if any(indicator in str(div) for indicator in ad_indicators):
            ad_tags.append(div)
    return ad_tags


# Retrieving xpath for elements
def xpath_soup(element):
    paths = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        paths.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    paths.reverse()
    return '/%s' % '/'.join(paths)


# Sorting visible elements
def sort_visible_elements(divs):
    xpaths = []
    for div in divs[:]:
        xpath = xpath_soup(div)
        xpaths.append(xpath)
    global invisible_ads
    invisible_ads = []
    global visible_ads
    visible_ads = []

    for i in range(len(divs)):
        try:
            element = driver.find_element_by_xpath(xpaths[i])  # this element is visible
            if element.is_displayed():
                visible_ads.append(divs[i])
            else:
                invisible_ads.append(divs[i])
        except NoSuchElementException:
            invisible_ads.append(divs[i])


# Appyling classifier to data for predicting type
def predict_type_visible(divs):
    """This function takes all divs provided in the open_for_divs function,
    applies the classifier to each divs, and counts the instances of each classes of types"""
    num = 1
    type_count = []
    for i in divs:
        wm = vec.fit_transform([str(i)])
        type_ = model.predict(wm)
        type_count.append(type_.item(0))
        num = num + 1
    global count_visible_better
    count_visible_better = type_count.count('better')
    global count_visible_popup
    count_visible_popup = type_count.count('popup')
    global count_visible_sticky
    count_visible_sticky = type_count.count('sticky')


def predict_type_invisible(divs):
    """This function takes all divs provided in the open_for_divs function,
    applies the classifier to each divs, and counts the instances of each classes of types"""
    num = 1
    type_count = []
    for i in divs:
        wm = vec.fit_transform([str(i)])
        type_ = model.predict(wm)
        type_count.append(type_.item(0))
        num = num + 1
    global count_invisible_better
    count_invisible_better = type_count.count('better')
    global count_invisible_popup
    count_invisible_popup = type_count.count('popup')
    global count_invisible_sticky
    count_invisible_sticky = type_count.count('sticky')


from xml.etree import ElementTree

tree = ElementTree.parse('./top500_newssites_0609.xml')
root = tree.getroot()

urls = []
titles = []
popularity_rankings = []

for listing in root.findall("Listing"):
    url = listing.find('DataUrl').text
    urls.append(url)
    title = listing.find('Title').text
    titles.append(title)
    popularity_ranking = listing.find('PopularityRank').text
    popularity_rankings.append(popularity_ranking)

data = zip(urls, titles, popularity_rankings)
df = pd.DataFrame(data, columns=["urls", "titles", "popularity_rankings"])

count_by_type = []

# driver.close()
driver = webdriver.Firefox()

# Classifier application of websites (by iteration)

for i in range(1, 516, 1):
    url = urls[i]
    name = titles[i]
    rank = popularity_rankings[i]
    open_url("https://" + url)
    url_index = URL.index(url)
    html = driver.page_source  # Get HTML source code
    divs = get_divs(html)
    div_count = len(divs)
    try:
        refine_divs(divs)
    except IndexError:
        print(url)
        pass
    get_ads(refined_divs)
    sort_visible_elements(ad_tags)
    num_invisible = len(invisible_ads)
    num_visible = len(visible_ads)
    predict_type_visible(visible_ads)
    predict_type_invisible(invisible_ads)

    count_by_type.append(
        {'URL_NO': url_index + 1, 'URL': url, "Website": name, "Popularity_Rank": rank, 'visible_ads': num_visible,
         'invisible_ads': num_invisible, 'better_visible': count_visible_better,
         'better_invisible': count_invisible_better, 'popup_visible': count_visible_popup,
         'popup_invisible': count_invisible_popup, 'sticky_visible': count_visible_sticky,
         'sticky_invisible': count_invisible_sticky})

print(len(count_by_type))

df = pd.DataFrame.from_dict(count_by_type)

df.to_csv("top500_newssites_advertising_practices.csv")

# Plotting advertising practices by websites

df.plot(kind='bar', x='URL_NO', y='worse_ads_visible', figsize=(20, 10), ylim=(0, 20))
plt.title("Number of Visible Worse Ads", fontsize=20)
plt.legend(fontsize=15)
plt.xticks([100, 200, 300, 400, 500], labels=[100, 200, 300, 400, 500], rotation=0)
plt.autoscale(tight=False)
df.plot(kind='bar', x='URL_NO', y='sticky_visible', color='red', figsize=(20, 10), ylim=(0, 20))
plt.title("Number of Visible Sticky Ads", fontsize=20)
plt.xticks([100, 200, 300, 400, 500], labels=[100, 200, 300, 400, 500], rotation=0)
plt.legend(fontsize=15)
plt.autoscale(tight=False)
df.plot(kind='bar', x='URL_NO', y='popup_visible', color='green', figsize=(20, 10), ylim=(0, 20))
plt.title("Number of Visible Pop-up Ads", fontsize=20)
plt.xticks([100, 200, 300, 400, 500], labels=[100, 200, 300, 400, 500], rotation=0)
plt.legend(fontsize=15)
plt.autoscale(tight=False)
plt.show()
