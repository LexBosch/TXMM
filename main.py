from pyyoutube import Api
import nltk
import socket
from math import ceil
import pandas
import json
from datetime import datetime, date

socket.setdefaulttimeout(30000)
nltk.download(["stopwords", "punkt", "vader_lexicon"])

API_KEY = None

if API_KEY is None:
    print("Please make sure a API key is inserted. See https://developers.google.com/youtube/v3/getting-started for more information.")
    raise KeyboardInterrupt


api = Api(api_key=API_KEY, timeout=300000)
stopwords = nltk.corpus.stopwords.words("english")

from nltk.sentiment import SentimentIntensityAnalyzer

FILE_TYPE="vlog"

def main():
    file = pandas.read_csv(f"videos_{FILE_TYPE}.txt", header=0)
    print(file)
    for index, row in file.iterrows():
        old_vid_id = row.values[0]
        new_vid_id = row.values[1]
        old_comments, _ = get_negativity(get_last_comments(old_vid_id), old=True)
        new_comments, _ = get_negativity(get_last_comments(new_vid_id))
        output_file = ({"old_video":{"id":old_vid_id, "sentiment":old_comments},
                            "new_video":{"id":new_vid_id, "sentiment":new_comments}
                            })

        with open(f"output_{FILE_TYPE}.json", "r") as file:
            data = json.load(file)

        data.append(output_file)

        with open(f"output_{FILE_TYPE}.json", "w") as file:
            json.dump(data, file)


def get_last_comments(video_id: str, amount: int =1000) -> list:
    all_comment_objects = api.get_comment_threads(text_format="plainText", video_id=video_id, count=None)
    oldest_comment_ids = all_comment_objects.items[-amount:]
    all_comment_ids = [comment.id for comment in oldest_comment_ids]

    sepperated_lists = []
    for i in range(0, ceil(len(all_comment_ids) / 50)):
        sepperated_lists.append(all_comment_ids[i * 50: (i + 1) * 50])

    all_comments = []
    for sublist in sepperated_lists:
        all_comments += api.get_comment_by_id(comment_id=sublist).items
    return all_comments


def get_negativity(comments, get_full_list: bool = False, old: bool =False) -> (float, dict):
    total_negative = 0
    full_list = []
    for comment in comments:
        if old:
            comment_age = datetime.strptime(comment.snippet.publishedAt[0:10], "%Y-%m-%d").date()
            dislike_removal = date(2021, 11, 6)
            if comment_age > dislike_removal:
                continue

        text = (comment.snippet.textOriginal.lower())
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(text)
        if sentiment["compound"] < -0.2:
            total_negative -= sentiment["compound"]
            if get_full_list:
                full_list.append({"text":comment, "sentiment":sentiment["compound"]})
    return (total_negative / len(comments)), full_list


if __name__ == '__main__':
    main()