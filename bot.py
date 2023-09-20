import time
import requests
import json
import bot_test
import util_markdown
import os

from urllib.parse import quote as urlencode

from main import ProducedNewsArticle, produce_article

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
        for update in updates['result']:
            process_update(update)
        print("Sleeping...")
        time.sleep(pool_time)

def process_update(update):
    if 'message' in update:
        log(update['message'])
        process_text_message(update['message'])

def process_text_message(message):
    chat_id = message['chat']['id']
    text = message['text']
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
    urls: list[str] = text.split('\n')
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


def send_message(chat_id, text: str, markdown=False):
    response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',params={'chat_id': chat_id, 'text': text, 'parse_mode': 'MarkdownV2' if markdown else None})
    return response.json()

def send_test_article(chat_id):
    send_article(chat_id, bot_test.test_article, bot_test.urls)

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
    
    sources_text = '\n\n'.join([
        get_sources_text(paragraph)
        for paragraph in article.content
    ])
    send_article(chat_id, "Explaining the sources...")
    send_message(chat_id, sources_text, markdown=True)

if __name__ == '__main__':
    print(get_me())
    assert TELEGRAM_TOKEN is not None
    loop_updates()