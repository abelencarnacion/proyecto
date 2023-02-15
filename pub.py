import json
import requests
import redis
URL = 'http://thestream.com' # not a real url obviously
red = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)
def stream():
    s = requests.Session()
    r = s.get(URL, stream=True)
    for line in r.iter_lines():
        if line:
            tweet_content = json.loads(line)
            username = tweet_content.get('username')
            hashtags = tweet_content.get('hashtags')
            red.publish('usernames', username)
            red.publish('hashtags', hashtags)
if __name__ == "__main__":
    while True:
        stream()