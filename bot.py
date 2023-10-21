import time
import requests
import json
import bot_test
import util_markdown
import os

from urllib.parse import quote as urlencode

from main import ProducedNewsArticle, produce_article
from google_news import extract_news_article, GoogleNewsCoverage

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

def log(message):
    print(message)


def get_me():
    response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe')
    return response.json()

def get_updates(last_update_id=None, timeout=30):
    response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?timeout={timeout}{"&offset="+str(last_update_id) if last_update_id else ""}',)
    return response.json()

def loop_updates():
    last_update_id = None
    pool_time = int(os.getenv('POOL_TIME', "1"))
    timeout = int(os.getenv('TIMEOUT', "0"))
    while True:
        updates = get_updates(
            last_update_id=None if last_update_id is None else last_update_id + 1,
            timeout=timeout
        )
        log(f"Got updates {len(updates['result'])}")
        if len(updates['result']) > 0:
            last_update_id = int(updates['result'][-1]['update_id'])
            log(f"Last update id {last_update_id}")
        skip = False
        for update in updates['result']:
            if 'message' in update and update['message']['text'] == '/skip':
                chat_id = update['message']['chat']['id']
                send_message(chat_id, "Skipped")
                skip = True
        if skip:
            continue
        
        for update in updates['result']:
            process_update(update)
        print("Sleeping...")
        time.sleep(pool_time)

def process_update(update):
    if 'message' in update:
        log(update['message'])
        process_text_message(update['message'])

last_sent_coverag: list[GoogleNewsCoverage] = None

def process_text_message(message):
    chat_id = message['chat']['id']
    text: str = message['text']
    from_user = message['from']
    name = from_user['first_name']
    log(f"Got message from {from_user['username']}: {text}")
    user_id = from_user['id']
    if user_id != 135806583:
        return send_message(chat_id, 'You are not allowed to use this bot!')
    if text == '/start':
        return send_message(chat_id, f'Hi {name}, send me a message with the urls you want to use to generate the post.')
    elif text == '/stop':
        return send_message(chat_id, f'Bye {name}')
    elif text == '/test_article':
        return send_test_article(chat_id)
    elif text == '/get_coverage':
        last_sent_coverage = send_coverage(chat_id)
        return
    elif last_sent_coverage is not None and text.startswith('/produce'):
        number = int(text[len('/produce'):])
        if number < 1 or number > len(last_sent_coverage):
            return send_message(chat_id, f'Invalid number {number}, please send me a valid number.')
        coverage: GoogleNewsCoverage = last_sent_coverage[number - 1]
        send_message(chat_id, f'Got coverage {number}, generating post...')
        send_generate_post(chat_id, [article.url for article in coverage.articles])
        return
    urls: list[str] = text.split('\n')
    return send_generate_post(chat_id, urls)

def send_generate_post(chat_id, urls: list[str]):
    for url in urls:
        if url.startswith('http'):
            log(f"Got url {url}")
        else:
            return send_message(chat_id, f'Invalid url {url}, please send me a valid url.')
    send_message(chat_id, f'Got {len(urls)} urls, generating post...')
    try:
        article = produce_article(urls)
    except Exception as e:
        send_message(chat_id, f'Error: {e}')
        return
    send_message(chat_id, f'Generated post!')
    send_message(chat_id, f'Please check the post and make sure it is correct. If it is not, please send me the correct urls and I will try again.')
    send_article(chat_id, article, urls)

def send_coverage(chat_id):
    send_message(chat_id, "Getting coverage...")
    news_coverages = extract_news_article(limit=3)
    send_message(chat_id, f"Got {len(news_coverages)} coverages")
    msg = 'I have found the following coverages:\n'
    for i, news_coverage in enumerate(news_coverages):
        msg += f"[{i + 1}] {len(news_coverage.articles)} articles\n"
        msg += '\n'.join([
            f"[{j + 1}] {util_markdown.escape(article.title)}" for j, article in enumerate(news_coverage.articles)
        ])
        msg += '\n'
    send_message(chat_id, msg)
    send_message(chat_id, "Please send me the number of the coverage you want to use.")
    return news_coverages

def send_message(chat_id, text: str, markdown=False):
    response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',params={'chat_id': chat_id, 'text': text, 'parse_mode': 'MarkdownV2' if markdown else None})
    return response.json()

def send_test_article(chat_id):
    return send_article(chat_id, bot_test.test_article, bot_test.urls)

def send_article(chat_id, article: ProducedNewsArticle, urls: list[str] ):
    def get_paragraph_text(paragraph: ProducedNewsArticle.ProducedParagraph):
        sources_text = ''.join([
            f'[\[{source.article_index + 1}\]]({util_markdown.escape(urls[source.article_index])})' for source in paragraph.sources
        ])
        return f"{util_markdown.escape(paragraph.text)} {sources_text}"
    paragraphs = [
        get_paragraph_text(paragraph)
        for paragraph in article.content
    ]
    paragraphs_text = '\n'.join(paragraphs)
    text_message = f'*{util_markdown.escape(article.title)}*\n\n{paragraphs_text}'
    send_message(chat_id, "Sending article...")
    send_message(chat_id, text_message, markdown=True)

    def get_sources_text(paragraph: ProducedNewsArticle.ProducedParagraph):
        sources_text = '\n'.join([
            f"[Source {source.article_index + 1}]({util_markdown.escape(urls[source.article_index])}):\n*Reason*:{util_markdown.escape(source.reason)}\n*Source*:{util_markdown.escape(' --- '.join(source.article_texts))}\n"
            for source in paragraph.sources
        ])
        return f"*Paragraph*:\n{util_markdown.escape(paragraph.text)}\n\n*Sources*:\n{sources_text}"
    
    sources_texts = [
        get_sources_text(paragraph)
        for paragraph in article.content
    ]
    send_message(chat_id, "Explaining the sources...")
    for sources_text in sources_texts:
        send_message(chat_id, sources_text, markdown=True)

if __name__ == '__main__':
    print(get_me())
    assert TELEGRAM_TOKEN is not None
    loop_updates()