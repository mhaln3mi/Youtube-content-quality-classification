import os
import pandas as pd 
import googleapiclient.discovery

def yt_api(id):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyArAXXQzyo8XBs5o5lm5aKL8_aRB_YDG1M"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part="id,snippet",
        maxResults=1000,
        order="relevance",
        videoId= id
    )
    response = request.execute()

    return response
response = yt_api("uhm5yVT8qvY")



def create_df():
  authorname = []
  comments = []
  for i in range(len(response["items"])):
    authorname.append(response["items"][i]["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"])
    comments.append(response["items"][i]["snippet"]["topLevelComment"]["snippet"]["textOriginal"])
  df_1 = pd.DataFrame(comments, index = authorname,columns=["Comments"])
  return df_1 
df_1 = create_df()
df_1.to_csv(r'C:\Users\wled3\ytdf5.csv')