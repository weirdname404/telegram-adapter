from pydantic import BaseModel
from typing import List, Type, Dict, Callable
from requests import Session
import os
import sys
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Webhook(BaseModel):
    """
    Telegram message text will be sent to a given url
    in a JSON format: {json_key: text}
    """
    url: str
    json_key: str


class TGAdapter(BaseModel):
    '''
    Listens to Telergam app updates and sends them to a given webhook.
    Webhook's response is sent back to the Telegram app.
    '''
    app_token: str
    webhook: Webhook
    webhook_session: Type[Session] = Session()
    tg_session: Type[Session] = Session()
    tg_api_url: str = "https://api.telegram.org/bot"

    def _get_updates(self, last_update_id: int, update_url: str, timeout: int=300) -> Dict:
        # incr the offset by 1 to get updates after the last one
        resp = self.tg_session.post(
                update_url, data={'timeout': timeout, 'offset': last_update_id + 1})

        if not resp:
            return []

        if resp.status_code != 200:
            logger.debug(f"Status code is not 200. {resp.text}")

        return resp.json()['result']

    @staticmethod
    def _get_values_to_text(d: Dict) -> str:
        s = ''
        c = 1
        for v in d.values():
            s = f"{s}{c}. {v}\n"
            c += 1

        return s

    def _get_webhook_request_func(self) -> Callable:
        url = self.webhook.url
        json_key = self.webhook.json_key
        session = self.webhook_session

        def send_webhook_request(text: str) -> Dict:
            res = session.post(url, data={json_key: text})
            if res.status_code != 200:
                logger.debug(f"Something wrong with a webhook. {res.text}")
                return {}
            return res.json()

        return send_webhook_request

    def run(self):
        get_update_url = f"{self.tg_api_url}{self.app_token}/getUpdates"
        send_msg_url = f"{self.tg_api_url}{self.app_token}/sendMessage"
        send_webhook_request = self._get_webhook_request_func()
        update_id = 0

        logger.info('Listening to updates...')
        while True:
            for update in self._get_updates(update_id, get_update_url):
                update_id = update['update_id']
                msg = update['message']
                webhook_resp = send_webhook_request(msg['text'])
                text = self._get_values_to_text(webhook_resp)
                self.tg_session.post(
                    send_msg_url, 
                    data={'chat_id': msg['chat']['id'], 'text': text}
                )


def main():
    app_token = os.environ.get('APP_TOKEN')
    webhook_url = os.environ.get('WEBHOOK')
    if app_token is None or webhook_url is None:
        logger.info("APP_TOKEN or WEBHOOK is not set in .env")
        logger.info("Exiting...")
        sys.exit()

    webhook = Webhook(url=webhook_url, json_key='question')
    tg_adapter = TGAdapter(app_token=app_token, webhook=webhook)
    tg_adapter.run()


if __name__ == "__main__":
    main()

