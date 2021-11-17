# from PIL import Image

import requests


def get_liveChatId(videoId, api_key, url='https://www.googleapis.com/youtube/v3/videos'):
    payload = dict(
        part='liveStreamingDetails',
        key=api_key,
        id=videoId,
    )
    return (
        requests
        .get(url, params=payload)
        .json()['items'][0]['liveStreamingDetails']['activeLiveChatId']
    )


def get_chat_messages(liveChatId, api_key, url='https://www.googleapis.com/youtube/v3/liveChat/messages'):
    payload = dict(
        part='id,snippet,authorDetails',
        textFormat='plainText',
        liveChatId=liveChatId,
        # maxResults=100,
        key=api_key,
    )
    r = requests.get(url, params=payload).json()
    messages = [
        {
            'id': message['id'],
            'text': message['snippet']['textMessageDetails']['messageText'],
            'displayName': message['authorDetails']['displayName'],
            'profileImageUrl': message['authorDetails']['profileImageUrl'],
        }
        for message in r['items']
    ]
    return messages, r['pollingIntervalMillis']


# def get_profileImage(url):
#     return Image.open(io.BytesIO(requests.get(url).content))
