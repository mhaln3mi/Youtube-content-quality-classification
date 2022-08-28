from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
from lib2to3.pgen2 import token
import os
from urllib import response
from dateutil import parser
import re
from googleapiclient.discovery import build
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import isodate
from sklearn.preprocessing import LabelEncoder


youtube = build('youtube', 'v3', developerKey='AIzaSyArAXXQzyo8XBs5o5lm5aKL8_aRB_YDG1M')



box = [['Name', 'Comments', 'Time', 'Likes', 'Reply Count']]

def scrape_comments_with_replies(id):
    data = youtube.commentThreads().list(part='snippet', videoId=id, maxResults='100', textFormat="plainText").execute()
        
    for i in data["items"]:
        name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
        comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
        published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']
        likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
        replies = i["snippet"]['totalReplyCount']
            
        box.append([name, comment, published_at, likes, replies])
            
        totalReplyCount = i["snippet"]['totalReplyCount']
            

    while ("nextPageToken" in data):
            
        data = youtube.commentThreads().list(part='snippet', videoId=id, pageToken=data["nextPageToken"],
                                             maxResults='100', textFormat="plainText").execute()
                                             
        for i in data["items"]:
            name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
            replies = i["snippet"]['totalReplyCount']

            box.append([name, comment, published_at, likes, replies])

            totalReplyCount = i["snippet"]['totalReplyCount']

                

    df = pd.DataFrame({'Name': [i[0] for i in box], 'Comments': [i[1] for i in box], 'Time': [i[2] for i in box],
                       'Likes': [i[3] for i in box], 'Reply Count': [i[4] for i in box]})
        
    sql_vids = pd.DataFrame([])

    sql_vids = sql_vids.append(df, ignore_index = True)

    return sql_vids
    


def cleaning_comments(comment):
  comment = re.sub("[😃|🤣|🤭|🤣|😁|🤭|❤️|👍|🏴|😣|😠|💪|🙏|😞|🌺|🌸|🌞|🌻|💐|💓|😥|💔|😪|😑|🏽|😢|😑|😇|💜|🪴|🙌🏻|🇨🇦|🕊|🕯|😭|😔|💙|🏼|✝|🇿]+",'',str(comment))
  comment = re.sub("[\:|\@|\)|\*|\.|\$|\!|\?|\,|\%|\"|\(|\-|\”|\#|\!|\/|\«|\»|\&|\n|\'|\;|\!|<|>|\'|\’|\\\\]+"," ",str(comment))
  return comment


lower = lambda x: x.lower()



nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

scores = []
ids = []


def get_video_details(youtube, video_ids):

    all_video_info = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute() 

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }
            video_info = {}
            video_info['video_id'] = video['id']

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)
    
    return pd.DataFrame(all_video_info)



def get_channel_stats(youtube, channel_ids):
    
    """
    Get channel stats
    
    Params:
    ------
    youtube: build object of Youtube API
    channel_ids: list of channel IDs
    
    Returns:
    ------
    dataframe with all channel stats for each channel ID
    
    """
    
    all_data = []
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()

    # loop through items
    for item in response["items"]:
        data = {'channelTitle': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'totalViews': item['statistics']['viewCount'],
                'totalVideos': item['statistics']['videoCount']     
        }
        
        all_data.append(data)
        
    return(pd.DataFrame(all_data))






with open('RFmodelFinal' , 'rb') as m:
   model = pickle.load(m)



app = Flask(__name__)

@app.route('/')
def test():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def home():
    vid_id = request.form['vid-id']
    ch_id = request.form['ch-id']

    ids.append(vid_id)
    df = scrape_comments_with_replies(vid_id)
    df.drop([0], axis=0, inplace=True)
    
    df['Comments'] = df['Comments'].apply(cleaning_comments)
    df['Comments'] = df['Comments'].apply(lower)

    #Create scores col
    df['Scores'] = df['Comments'].apply(lambda x: sid.polarity_scores(x))

    #Create compund score
    df['Compound'] = df['Scores'].apply(lambda score_dict: score_dict['compound'])


    g = df['Compound'].sum()
    d = df['Compound'].count()

    total_score = g / d    
    scores.append(total_score)

    df1 = pd.DataFrame(list(zip(ids, scores)), columns =['video_id', 'avg polarity score']) 

    df2 = get_video_details(youtube, ids)

    ch = get_channel_stats(youtube, [ch_id])
    
    dff = pd.merge(df1, df2)

    dff = pd.merge(dff, ch)

    dff = dff.fillna(0)
    dff['publishedAt'] = dff['publishedAt'].apply(lambda x: parser.parse(x)) 
    dff['pushblishYear'] = dff['publishedAt'].apply(lambda x: x.strftime("%Y"))
    numeric_cols = ['viewCount', 'likeCount', 'commentCount', 'pushblishYear']
    dff[numeric_cols] = dff[numeric_cols].apply(pd.to_numeric, errors = 'coerce', axis = 1)

    dff['durationSecs'] = dff['duration'].apply(lambda x: isodate.parse_duration(x))
    dff['durationSecs'] = dff['durationSecs'].astype('timedelta64[s]')
    dff['tagCount'] = dff['tags'].apply(lambda x: 0 if x is np.nan else len(x))
    dff['title length'] = dff['title'].apply(lambda x: 0 if x is np.nan else len(x))
    dff['description length'] = dff['description'].apply(lambda x: 0 if x is np.nan else len(x))
    new_cols = ["channelTitle","viewCount",'likeCount','commentCount','definition','caption','subscribers','totalViews','totalVideos','avg polarity score','pushblishYear','durationSecs','tagCount','title length','description length']
    dff=dff[new_cols]
    #or
    dff=dff.reindex(columns=new_cols)

    le = LabelEncoder()

    catg = ['channelTitle', 'definition', 'caption']
    dff[catg] = dff[catg].apply(le.fit_transform)

    #model prediction

    pred = model.predict(dff)

    if pred[0] == 1:
        return render_template('result1.html')
    else:
        return render_template('result2.html')




@app.route('/report')
def report():
    return render_template('report.html')

if __name__ == "__main__":
    app.run(debug=True)
#     from waitress import serve
#     serve(app, host="0.0.0.0", port=8080)