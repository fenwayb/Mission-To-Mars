# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_p = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_image(browser)
    }
    # stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    #scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:

        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
  
 
    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    return df.to_html()

def mars_image(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    #this finds how many items tags there are to loop through in the following code
    items_count = []
    html = browser.html
    mars_soup = soup(html, 'html.parser')
    results = mars_soup.find('div', class_='collapsible results')
    items = len(mars_soup.find_all('div', class_='item'))
    count = 0
    while len(items_count) < items:
        count = count+1
        items_count.append(count)
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    img_url_list = []
    img_title_list = []
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for x in items_count:
        browser.find_by_xpath(f'/html/body/div[1]/div[1]/div[2]/section/div/div[2]/div[{x}]/div/a').click()
        img_url = browser.find_by_xpath('/html/body/div[1]/div/div[2]/div/ul/li[1]/a')["href"]
        img_url_list.append(img_url)
        img_title = browser.find_by_xpath('/html/body/div[1]/div/div[3]/h2').text
        img_title_list.append(img_title)
        browser.back()

    for item in img_url_list:
        keys = ["img_url", "title"]
        x = img_url_list.index(item)
        values = [img_url_list[x], img_title_list[x]]
        hemispheres = dict(zip(keys, values))
        hemisphere_image_urls.append(hemispheres)

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

