# -*- coding: utf-8 -*-
from oath_key import *
import json, time, calendar, re

# tweet["created_at"]の表示形式変換
def time_convert(created_at):
    time_utc = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    return time.strftime("%Y/%m/%d %H:%M:%S", time_local)

# ツイートの取得
def tweet_search(max_id, oath_key_dict):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"    # タイムライン取得URL
    params = {
        "screen_name":analyze_id(),
        "count":200,
        "max_id":max_id,
        "result_type":"recent",
        "exclude_replies":"false",
        "include_rts":"false"
    }
    # OAuthでツイート取得
    oath = create_oath_session(oath_key_dict)
    req = oath.get(url, params = params)
    if req.status_code == 200:
        tweets = json.loads(req.text)    # レスポンスはJSON形式なので parse する
    else:
        print ("Error: %d" % req.status_code)
    return tweets

# ツイートの分割
def tweet_split(tweet_text):
    match_song = re.search("-",tweet_text)
    match_difficulty = re.search("\(",tweet_text)
    match_score = re.search("\)",tweet_text)
    match_percent = re.search("%",tweet_text)
    song_no = match_song.start()
    difficulty_no = match_difficulty.start()
    score_no = match_score.start()
    percent_no = match_percent.start()
    song = tweet_text[song_no+2:difficulty_no]
    difficulty = tweet_text[difficulty_no+1:score_no]
    score = tweet_text[score_no+2:percent_no+2]
    return(song, difficulty, score)

# 取得ツイートからハッシュタグの有無を調査-->からの表示
def tweet_display(tweets):
    for tweet in tweets:
        if len(tweet["entities"]["hashtags"]) == 0:
            pass
        else:
            if tweet["entities"]["hashtags"][0]["text"] == "Deemo":
                print(time_convert(tweet["created_at"]))
                print(tweet["text"])
#                print(tweet["entities"]["hashtags"][0]["text"])    # <--[0]を突っ込んだらできたんだけどなんで？？
                song, difficulty, score = tweet_split(tweet["text"])
                print(song)
                print(difficulty)
                print(score)
#                print(tweet["id"])
            else:
                pass
        tweet_id = tweet["id"]
    return tweet_id

# APIに16回(3200件分)アクセスするループ部分
def main():
    times = 0
    max_id = None
    while times < 17:
        tweets = tweet_search(max_id, oath_key_dict)
        tweet_id = tweet_display(tweets)
        max_id = tweet_id - 1
#        print(max_id)
        times += 1

if __name__ == "__main__":
    main()

# とってきたツイートを正規表現で切る(「ツイート日付時間・曲名・難易度・スコア」の4つ。ポエムは捨て去る)
# 3200件以上取得する方法探す(Forで回す？) --> 200ずつ取るなら16回まわす
# chart.jsかD3.jsで表示する(もしかしたらJSON形式に戻さないとかも)
# Flask側書く()