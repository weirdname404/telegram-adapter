**Description**

This script was designed to work as a daemon that does following:

1. Endlessly requests updates from specific Telegram app via long polling;
2. Sends received updates to the given __WEBHOOK__ url;
3. Waits for __WEBHOOK's__ response, to send it back to the given Telegram app.

**Steps to start the script**

- Add to your `.env` file values of APP_TOKEN (TG app token) and WEBHOOK (url)
- `docker build -t tg-adapter .`
- `docker run --env-file=.env --name tg-adapter -d tg-adapter:latest`
