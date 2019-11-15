from pydantic import BaseModel
from typing import List, Type, Dict
from requests import Session
import os
import sys
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Webhook(BaseModel):
    url: str
    json_key: str = os.environ.get('WEBHOOK_POST_KEY', 'question')


class TGAdapter(BaseModel):
    '''
    Listens to TG app updates and sends them to the webhook url,
    webhook's response adapter returns to the TG app
    '''
    app_token: str
    webhook: Webhook
    webhook_session: Type[Session] = Session()
    tg_session: Type[Session] = Session()
    tg_api_url: str = "https://api.telegram.org/bot"

    def _get_updates(self, last_update_id: int, update_url: str, timeout: int=300) -> Dict:
        # incr the offset by 1 to get updates after the last one
        resp = self.tg_session.post(
                update_url, data={'timeout': timeout, 'offset': last_update_id + 1}
                )
        if not resp:
            return []

        if resp.status_code != 200:
            logger.info(f"Status code is not 200. {resp.text}")

        return resp.json()['result']

    def _send_reply(self, api_url: str, data: Dict) -> None:
        self.tg_session.post(api_url, data=data)

    @staticmethod
    def _get_values_to_text(d: Dict) -> str:
        s = ''
        c = 1
        for v in d.values():
            s = f"{s}{c}. {v}\n"
            c += 1

        return s

    def _send_webhook_request(self, text: str) -> Dict:
        url = self.webhook.url
        json_key = self.webhook.json_key

        resp = self.webhook_session.post(
                url, data={json_key: text}
            )

        return resp.json()

    def run(self):
        api_update_url = f"{self.tg_api_url}{self.app_token}/getUpdates"
        api_send_url = f"{self.tg_api_url}{self.app_token}/sendMessage"

        update_id = 0
        logger.info('Listening to updates...')
        while True:
            for update in self._get_updates(update_id, api_update_url):
                update_id = update['update_id']
                msg = update['message']
                webhook_resp = self._send_webhook_request(msg['text'])
                text = self._get_values_to_text(webhook_resp)
                self.tg_session.post(
                    api_send_url, 
                    data={'chat_id': msg['chat']['id'], 'text': text}
                )


def main():
    app_token = os.environ.get('APP_TOKEN')
    webhook_url = os.environ.get('WEBHOOK')
    if app_token is None or webhook_url is None:
        logger.info("APP_TOKEN or WEBHOOK is not set in .env")
        logger.info("Exiting...")
        sys.exit()

    webhook = Webhook(url=webhook_url)
    tg_adapter = TGAdapter(app_token=app_token, webhook=webhook)
    tg_adapter.run()


if __name__ == "__main__":
    main()

