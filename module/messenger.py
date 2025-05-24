# from dotenv import load_dotenv
# import asyncio
# import os
import telegram
import json
import requests

async def send_telegram_message(token, chat_id, message):
    """텔레그램 메시지를 보냅니다.
    
    :param token: 텔레그램 봇 토큰 값
    :param chat_id: 메시지를 수신할 챗 아이디(조회 방법: 봇과 적어도 한 번 대화한 다음 https://api.telegram.org/bot봇토큰값/getUpdates 접속 후 "message": { "id" } 속성 값 확인)
    :return: None <class 'NoneType'>
    """
    bot = telegram.Bot(token)
    await bot.send_message(chat_id=chat_id, text=message)
    

def send_discord_message(webhook_url, message):
    """디스코드 웹훅을 사용하여 메시지를 보냅니다.

    :param webhook_url: 디스코드 채널 웹훅 URL
    :param message: 보내려는 메시지(마크다운 일부 형식도 가능함)
    :return: None <class 'NoneType'>
    """
    headers = { 'Content-Type': 'application/json', }
    data = { 'content': message, }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 204:
        print('Message successfully sent to Discord channel.')
    else:
        print(f'Failed to send message to Discord channel. Status code: {response.status_code}')

# if __name__ == "__main__":
    # asyncio.run(send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "Message"))
    # send_discord_message("https://discord.com/api/webhooks/your_webhook_url_here", "Message")