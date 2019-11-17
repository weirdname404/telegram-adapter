**Description**

This script was designed to work as a daemon that does following:

1. Endlessly requests updates from specific Telegram app via long polling;
2. Sends received updates to the given __WEBHOOK__ url;
3. Waits for __WEBHOOK's__ response, to send it back to the given Telegram app.

**Steps to start the script**

0. Add to your `.env` file values of APP_TOKEN (TG app token) and WEBHOOK
1. docker build -t tg-adapter .
2. docker run --env-file=.env --name tg-adapter -d tg-adapter:latest
