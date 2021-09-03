# -*- coding: utf-8 -*-
import re
import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request

class youtube_client:
    youtube_pattern = re.compile("http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?")

    def __init__(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

        scopes = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"]
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secrets.json"

        credentials = None
        if os.path.exists('credentials.pickle'):
            with open('credentials.pickle', 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("Refreshing Access token...")
                credentials.refresh(Request())
            else:
                print("Fetching new tokens...")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=scopes)
   
                flow.run_local_server(host='localhost', port=8080, prompt="consent", authorization_prompt_message='')#
                
                credentials = flow.credentials
                
                with open("credentials.pickle", "wb") as f:
                    print("saving credentials...")
                    pickle.dump(credentials, f)


        self.youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    def get_playlist_id_by_name(self, name):
        request = self.youtube.playlists().list(
        part="snippet, id",
        maxResults=25,
        mine=True
        )
        response = request.execute()

        matches = {}
        for item in response["items"]:
            playlist_title = item["snippet"]["title"]
            if name in playlist_title:
                matches[item["id"]] = playlist_title 

        return matches

    def list_videos_in_playlist(self, playlist_id):
        videos_in_playlist = self.youtube.playlistItems().list(part="status, contentDetails, snippet", playlistId=playlist_id)
        response = videos_in_playlist.execute()
        return [(item["contentDetails"]["videoId"], item["snippet"]["title"]) for item in response['items']]
    
    def add_video_to_playlist(self, playlist_id, video_id):
        playList_resource_template = {"kind": "youtube#playlistItem", "snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId":  video_id}}}
        print("now adding new song to playlist")
        add_to_playlist = self.youtube.playlistItems().insert(part="snippet", body=playList_resource_template)
        response = add_to_playlist.execute()

        return response["snippet"]['title']
    
    @staticmethod
    def get_video_ids(message):
        ids = []
        for sub_msg in message.split(' '):
            sub_msg = sub_msg.strip("/")
            for m in youtube_client.youtube_pattern.findall(sub_msg):
                if m not in ids:
                    ids.append(m[0])
                
        return len(ids) > 0, ids 

def url_tests():
    urls = ["https://www.youtube.com/watch?v=clKdNG_ZtXI&list=PL2qUo84aqmErtH3eSgzJ_bEXyYY_B_bFz&index=5", "asdasdasd asdfsdf", "https://youtu.be/qnYHA9saUN1 https://youtu.be/qnYHA9saUN0", "https://youtu.be/qnYHA9saUN0", "https://www.youtube.com/watch?v=qnYHA9saUN0", "https://www.youtube.com/watch?v=qnYHA9saUN0 asdasd", "https://www.youtube.com/watch?v=qnYHA9saUN0/", "https://www.youtube.com/watch?v=qnYHA9saUN0/aasd"]
    for i, url in enumerate(urls):
        noids, ids = youtube_client.get_video_ids(url)
        try:
            assert(noids == 1)
            print(ids)
        except:
            print("NO VALID URL FOUND: ", url)


if __name__ == "__main__":
    url_tests()
