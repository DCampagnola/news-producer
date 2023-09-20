import functools
import json
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import openai
from openai.error import InvalidRequestError, APIConnectionError, RateLimitError
from typing import List, Optional, Union
from pydantic import BaseModel, Field




class ProducedNewsArticle(BaseModel):
    class ProducedParagraph(BaseModel):
        class Source(BaseModel):
            article_texts: List[str] = Field(
                description="The text of the news article that is used as a source to write the paragraph.",
                examples=[
                    ["Jack said that he was going to the store.", "He replied, \"I am going to the store.\""],
                ],
                min_length=1,
            )
            reason: str = Field(
                examples=["In this section, you can find the answer to the question"],
                description="The reason why the news article is used as a source.",
            )
            article_index: int = Field(
                examples=[0, 1],
                description="The index in the list of news articles.",
                ge=0,
            )
        text: str = Field(description="The text of the paragraph. The length should be between 10 to 20 words.")
        sources: List[Source] = Field(description="The news article sources of the paragraph.", min_length=0,)
    title: str = Field(description="The title of the news article. The length should be between 10 to 20 words.")
    content: List[ProducedParagraph] = Field(description="The content of the news article. The length should be between 100 to 200 words.")

def produce_article(article_urls: List[str], language = 'English'):
    assert len(article_urls) > 0
    options = Options()
    options.headless = True
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-gpu')
    driver = webdriver.Firefox(
        options=options,
    )
    news_articles: List[NewsArticle] = []
    for url in article_urls:
        news_articles.append(extract_news_article(url, driver=driver))
    output = openai.ChatCompletion.create(
        messages=[
            {
                "role": "system",
                "content": f"Given news articles from the user, please produce a three paragraph article in {language} that combines the news articles. It must use the sources and be neutral and factual without any opinions. The length should be between 100 and 200 words. Multiple paragraphs citing the same sources are allowed. Paragraphs with no sources are allowed. Change the wording of the paragraphs as much as you want to avoid copyright issues, but keep the meaning the same."
            },
            *[
                {
                    "role": "user",
                    "content": f"""{article.title}\n{article.content}\n"""
                }
                for article in news_articles
            ]
        ],
        functions=[
            {
                "name": "produce_news_article",
                "parameters": ProducedNewsArticle.model_json_schema()
            }
        ],
        function_call={"name": "produce_news_article"},
        model="gpt-4",
    )
    output = json.loads(output.choices[0]["message"]["function_call"]["arguments"])
    produced_article = ProducedNewsArticle(**output)
    driver.close()
    driver.quit()
    return produced_article

class NewsArticle(BaseModel):
    title: str
    content: str
    news_source: str
    date: str

@functools.lru_cache
def extract_news_article(
        url: str,
        driver: webdriver.Firefox,
):
    driver.get(url)
    title = driver.title
    content = driver.find_element(By.TAG_NAME, "body").text
    retry = True
    model = "gpt-3.5-turbo"
    while retry:
        try:
            output = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": "This is a news article, please extract the title, content, news source, and date."
                    },
                    {
                        "role": "user",
                        "content": f"""{title}\n{content}"""
                    },
                ],
                temperature=0,
                functions=[
                    {
                        "name": "extract_news_article",
                        "parameters": NewsArticle.model_json_schema()
                    }
                ],
                function_call={"name": "extract_news_article"},
                model=model,
            )
            if output.choices[0]['finish_reason'] != "stop" and model == "gpt-3.5-turbo":
                retry = True
                model = "gpt-3.5-turbo-16k"
                continue
            else:
                retry = False
            output = json.loads(output.choices[0]["message"]["function_call"]["arguments"])
            return NewsArticle(**output)
        except InvalidRequestError as e:
            if e.code == 'context_length_exceeded' and model == "gpt-3.5-turbo":
                retry = True
                model = "gpt-3.5-turbo-16k"
                continue
            raise e
        except RateLimitError as e:
            print("Rate limit error, retrying in 60 seconds...")
            time.sleep(60)
            continue
        except APIConnectionError as e:
            print("API connection error, retrying in 2 seconds...")
            time.sleep(2)
            continue

if __name__ == "__main__":
    produce_article([
        "https://thehill.com/opinion/international/4210108-biden-addresses-a-world-skeptical-of-yet-desperately-needing-us-leadership/",
        "https://abcnews.go.com/Politics/speaker-mccarthy-plans-confront-zelenskyy-ukraine-funding/story?id=103313355"
    ])