
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from typing import NamedTuple

class NewsArticle(NamedTuple):
    title: str
    url: str

class GoogleNewsCoverage(NamedTuple):
    articles: list[NewsArticle]

google_news_world_topic_url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"

def extract_news_article(limit: int = None) -> NewsArticle:
    options = Options()
    options.headless = True
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-gpu')
    driver = webdriver.Firefox(
        options=options,
    )
    try:
        news = get_news(driver, limit=limit)
        return news
    except Exception as e:
        print(f'Error: {e}')
        raise e
    finally:
        driver.quit()

def get_news(driver: webdriver.Firefox, limit: int = None) -> list[GoogleNewsCoverage]:
    driver.get(google_news_world_topic_url)
    cookie_button = driver.find_element(By.XPATH, "//form[2]/div/div/button/span")
    if cookie_button:
        cookie_button.click()
    news_articles_bulk = driver.find_elements(By.XPATH, "//*[@id=\"yDmH0d\"]/c-wiz/div/main/c-wiz/c-wiz/c-wiz")
    print(f"Got news articles bulk {len(news_articles_bulk)}")
    result: list[GoogleNewsCoverage] = []
    for news in news_articles_bulk:
        news_articles = news.find_elements(By.XPATH, ".//article")
        n: list[NewsArticle] = []
        print(f"Got news articles {len(news_articles)}")
        for news_article in news_articles:
            is_video = len(news_article.find_elements(By.XPATH, ".//*[name()='svg']")) > 1
            print(f"Is video {is_video}")
            if is_video:
                continue
            news_title = news_article.find_element(By.XPATH, ".//h4")
            print(f"Got news title {news_title.text}")
            news_article.click()
            # Should be in a new tab
            
            print(f"Clicked news title {news_article}")
            driver.switch_to.window(driver.window_handles[-1])
            # wait for the page to load and the redirect chain to finish
            try:
                WebDriverWait(driver, 60).until(lambda d: d.execute_script('return document.readyState') == 'complete' and 'google.com' not in d.current_url)
            except:
                print("Timeout")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue


            news_url = driver.current_url
            if news_url.startswith("https://www.google.com/url?q="):
                print(f"Got google news url {news_url}")
                news_url = news_url[len("https://www.google.com/url?q="):]
                news_url = news_url.split("&")[0]
            if "google.com" in news_url or "consent" in news_url:
                print(f"Skipping news url {news_url}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            print(f"Got news url {news_url}")
            # close the tab
            driver.close()
            # switch back to the main tab
            driver.switch_to.window(driver.window_handles[0])
            n.append(NewsArticle(news_title.text, news_url))
        if len(n) > 1:
            result.append(GoogleNewsCoverage(n))
        if limit and len(result) >= limit:
            break
    return result

if __name__ == '__main__':
    options = Options()
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-gpu')
    driver = webdriver.Firefox(
        options=options,
    )
    news = get_news(driver, limit=3)
    print(f"Got news {len(news)}")
    print("Coverage of today's news:")
    for coverage in news:
        print(f"Coverage of {len(coverage.articles)} articles:")
        for article in coverage.articles:
            print(f"{article.title}: {article.url}")
    driver.quit()