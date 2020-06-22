from flask import Flask, request
import telegram
from config import TOKEN, URL, PORT
import asyncio
from pyppeteer import launch


app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)



async def make_screenshot(url, image):
    browser = await launch(headless=True)
    page = await browser.newPage()

    await page.goto(url)
    image = await page.screenshot({'path': 'screen.png', 'fullPage': True})
    await browser.close()


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    """
    This function describes the behaviour of telegram bot according to request sent by user
    """
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    msg_id = update.message.message_id
    text = str(update.message.text.encode('utf-8').decode())
    print("Got message:", text)

    if text == "/start":
        bot_welcome = """
           Welcome to Screenshooting bot.
           The bot obtains url from user and provides printscreen of requested page.
           Please use following command:
           /show your_url - to obtain the screenshot of requested page, where your_url is the link to the site in format 
           http://full_link or https://full_link
           """
        bot.send_message(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    elif text.startswith("/show"):
        image = 0
        url_requested = text.split()
        if len(url_requested) != 2:
            warning_message = "There should be 2 entries with 1 blank space between them: 1) /show, 2) your_url. " \
                              "Please enter /start again and subsequently use command /show your_url"
            bot.send_message(chat_id=chat_id, text=warning_message, reply_to_message_id=msg_id)

        # elif not url_requested[1].startswith("http://") or not url_requested[1].startswith("https://"):
        #     warning_message = "You've used wrong url format. Please enter your url in format http://full_link or " \
        #                       "https://full_link"
        #     bot.send_message(chat_id=chat_id, text=warning_message, reply_to_message_id=msg_id)
        asyncio.get_event_loop().run_until_complete(make_screenshot(url_requested[1], image))
        bot.send_message(chat_id=chat_id, text="Screenshot made", reply_to_message_id=msg_id)
        bot.send_message(chat_id=chat_id, text=image, reply_to_message_id=msg_id)
        #bot.send_photo(chat_id=chat_id, photo=open('screen.png', 'rb'), reply_to_message_id=msg_id)

    else:
        unresolved_command = "There was a problem with the command you've used. " \
                             "Please enter /start to get info on commands available"
        bot.send_message(chat_id=chat_id, text=unresolved_command, reply_to_message_id=msg_id)

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


if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", threaded=True, debug=True)