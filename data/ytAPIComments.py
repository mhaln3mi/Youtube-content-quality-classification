from lib2to3.pgen2 import token
import os
from urllib import response
import pandas as pd 

from googleapiclient.discovery import build
youtube = build('youtube', 'v3', developerKey=os.environ.get('api_key'))



box = [['Name', 'Comments', 'Time', 'Likes', 'Reply Count']]

#Eudereka, Programming with Mosh, freeCodeCamp
code_lang = [
    {"id":"BpPJxtOk8uw"}
]

# sql_vids = pd.DataFrame([])


for id_code in code_lang:
    def scrape_comments_with_replies():
        data = youtube.commentThreads().list(part='snippet', videoId=id_code['id'], maxResults='100', textFormat="plainText").execute()
        
        for i in data["items"]:
            name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
            replies = i["snippet"]['totalReplyCount']
            
            box.append([name, comment, published_at, likes, replies])
            
            totalReplyCount = i["snippet"]['totalReplyCount']
            

        while ("nextPageToken" in data):
            
            data = youtube.commentThreads().list(part='snippet', videoId=id_code['id'], pageToken=data["nextPageToken"],
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

        sql_vids.to_csv('comments.csv')
    
    scrape_comments_with_replies()



