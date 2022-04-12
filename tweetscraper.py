import tweepy #https://github.com/tweepy
import csv
import pandas as pd
import re

def get_all_tweets(screen_name):
  #Twitter API credentials

  consumer_key = ""
  consumer_secret = ""
  access_key = ""
  access_secret = ""

  #authorize twitter, initialize tweepy
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)
  api = tweepy.API(auth)

  alltweets = []
  new_tweets = api.user_timeline(screen_name = screen_name,count=200)

  alltweets.extend(new_tweets)

  oldest = alltweets[-1].id - 1

  while len(new_tweets) > 0:
    print(f'getting tweets before {oldest}')

    new_tweets = api.user_timeline(screen_name = screen_name, count=200, max_id=oldest)

    alltweets.extend(new_tweets)

    oldest = alltweets[-1].id - 1
    print(f"...{len(alltweets)} tweets downloaded so far")

  outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]


  with open(f'new_{screen_name}_tweets.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'created_at', 'text'])
    writer.writerows(outtweets)

  pass

def clean_csv(fname='new_SICKOFWOLVES_tweets.csv'):
  df = pd.read_csv(fname)
  df = df.dropna()
  df = df[~df['text'].str.contains('STORE')]
  df['text'] = df['text'].str.replace('\n', ' ')
  df['text'] = df['text'].apply(lambda x:
    re.split('https:\/\/.*', str(x))[0])

  df['text'] = df['text'].apply(lambda x:
    ''.join([' ' if ord(i) < 32 or ord(i) > 126
      else i for i in x]))

  df['text'].to_csv('titles.csv', index=False, header=False)

