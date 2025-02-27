import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

app = FastAPI()

class TrackSearchRequest(BaseModel):
    track_name: str
    artist_name: str

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/search-tracks/")
def search_tracks(request: TrackSearchRequest):
    try:
        # Spotify API で曲を検索（最大5件）
        results = sp.search(q=f'artist:"{request.artist_name}" track:"{request.track_name}"', type='track', limit=5)
        tracks = results['tracks']['items']

        # 候補が見つからなかった場合
        if not tracks:
            raise HTTPException(status_code=404, detail="該当する曲が見つかりませんでした。")

        # 取得した曲情報を整形して返す
        track_list = []
        for track in tracks:
            track_list.append({
                "track_name": track['name'],
                "artist_name": ', '.join([artist['name'] for artist in track['artists']]),
                "album": track['album']['name'],
                "release_date": track['album']['release_date'],
                "spotify_url": track['external_urls']['spotify'],
                "preview_url": track.get('preview_url', None)
            })

        return {"tracks": track_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))