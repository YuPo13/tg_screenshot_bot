from flask import Flask, request
import telegram
import time
from venv.env import TOKEN, URL, PORT
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)


def make_screenshot(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-maximized')

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.get(url)
    time.sleep(5)

    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    screenshot_name = "screenshot.png"
    screenshot = driver.find_element_by_tag_name("body").screenshot(screenshot_name)

    driver.quit()
    return screenshot


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    """
    This function describes the behaviour of telegram bot according to request sent by user
    """
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    msg_id = update.message.message_id
    text = str(update.message.text.encode('utf-8').decode())

    if text == "/start":
        bot_welcome = """
           Welcome to Screenshooting bot.
           The bot obtains url from user and provides printscreen of requested page.
           Please use following command:
           /show your_url - to obtain the screenshot of can telegram bot remember deployment toolrequested page, where your_url is the link to the site in format 
           http://full_link or https://full_link
           """
        bot.send_message(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    elif text.startswith("/show"):
        url_requested = text.split()
        if len(url_requested) != 2:
            warning_message = "There should be 2 entries with 1 blank space between them: 1) /show, 2) your_url. " \
                              "Please use command /show your_url"
            bot.send_message(chat_id=chat_id, text=warning_message, reply_to_message_id=msg_id)
            return "Wrong entry"

        elif not url_requested[1].startswith("http://") or not url_requested[1].startswith("https://"):
            warning_message = "You've used wrong url format. Please enter your url in format http://full_link or " \
                              "https://full_link"
            bot.send_message(chat_id=chat_id, text=warning_message, reply_to_message_id=msg_id)
            return "Wrong entry"

        else:
            make_screenshot(url_requested[1])
            bot.send_photo(chat_id=chat_id, photo=open('screenshot.png', 'rb'), reply_to_message_id=msg_id)

    else:
        unresolved_command = "There was a problem with the command you've used. " \
                             "Please enter /start to get info on commands available"
        bot.send_message(chat_id=chat_id, text=unresolved_command, reply_to_message_id=msg_id)
        return "Wrong entry"

    return "ok"


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    """
    This function sets webhook
    """
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/', methods=['GET'])
def index():
    return '.'


# make_screenshot("https://gotoshop.ua/uk/kiev/shops/114-prospekt-lisovijj-9/")

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", threaded=True, debug=True)
