import ssl

import certifi
from slack_sdk import WebClient


class SlackAPI:
    def __init__(self, token):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(token=token, ssl=ssl_context)

    def get_channel_id(self, channel_name: str):
        """
        retrieve Slack channel id
        """
        result = self.client.conversations_list()
        channels = result.data["channels"]
        channel_list = list(filter(lambda c: c["name"] == channel_name, channels))
        if channel_list:
            channel = channel_list[0]
            channel_id = channel["id"]
            return channel_id

    def get_message_ts(self, channel_id: str, message: str):
        """
        retrieve message at channel
        message_ts 를 찾아오는 함수입니다.
        message는 메세지 내용입니다.
        """
        result = self.client.conversations_history(channel=channel_id)
        messages = result.data["messages"]
        retrieved_message_list = list(filter(lambda m: m["text"] == message, messages))
        if retrieved_message_list:
            retrieved_message = retrieved_message_list[0]
            message_ts = retrieved_message["ts"]
            return message_ts

    def post_thread_message(self, channel_id: str, message_ts, message: str):
        """
        슬랙 채널 내 메세지의 Thread에 댓글 달기
        """
        response = self.client.chat_postMessage(
            channel=channel_id, text=message, thread_ts=message_ts
        )
        return response

    def send_slack_message(self, channel_id: str, message: str):
        """
        send Slack message
        """
        response = self.client.chat_postMessage(channel=channel_id, text=message)
        return response
