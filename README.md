# Youtube-comments-sentiment-analysis
Capstone project for MISK-DSI 

### Introduction
In this project, my goal is to create a Machine Learning model to classify Youtube videos based on content quality into two classes: Reputable, and non Reputable. My aim is to make the process of finding good tutorials easier for everyday users and researchers.

### Data
I fetched the data using Youtube API, you can find the code I used to do that in the ```data``` folder. In this project I only collected data for different tutorials on Youtube.

#### Data dictionary:

| Variable      | Description |
| ----------- | ----------- |
| video_id    | The id of the Youtube video.       |
| channelTitle   | Name of the channel.       |
| title  | Title of the video.        |
| description   | The video description.        |
| tags   | List of tags in the video description.        |
| publishedAt   | The publish date of the video.         |
| viewCount   | Views of the video.       |
| likeCount   | Likes of the video.        |
| commentCount   | Number of comments on the video.      |
| duration   | The duration of the video.        |
| definition   | The video quality definition.       |
| caption   | Whether the video has caption or not.       |
| subscribers   | Number of subscribers the channel has.      |
| totalViews   | Total number of views the channel has.      |
| totalVideos   | Total number of videos the channel uploaded.      |
| avg polarity score   | The average polarity score for the comments of the video.      |
| Label   | Label of the video as Reputable or not.      |
