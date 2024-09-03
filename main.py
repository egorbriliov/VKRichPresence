import time
import requests
import vk_api
from pypresence import Presence
import os
from dotenv import load_dotenv

load_dotenv()
VK_TOKEN = os.getenv('VK_TOKEN')


class Discord:
    """Отвечает за активность в Discord"""

    def __init__(self, discord_client_id: int):
        self.__discord_rich_presence: Presence = Presence(client_id=discord_client_id)
        self.__track = None
        self.__connect()

    def __connect(self):
        self.__discord_rich_presence.connect()

    def __disconnect(self):
        self.__discord_rich_presence.clear()

    def update(self, track: dict):
        if track:
            if track != self.__track:
                self.__track = track
                try:
                    large_image = track['album']['thumb']['photo_1200']
                    state = track['artist']
                    details = track['title']
                    url = track['release_audio_id']
                    duration = track['ads']['duration']
                    self.__discord_rich_presence.update(
                        large_text=str(details),
                        state=state,
                        details=details,
                        start=int(time.time()),
                        end=int(time.time()) + int(duration),
                        large_image=large_image,
                        buttons=[{"label": "Listen to", "url": f"https://vk.com/audio{url}"}]
                    )
                    print("New update")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                print("Current track has playing")
        else:
            self.__track = None
            self.__disconnect()
            print("Track not playing")


class VK:
    def __init__(self, token: str):
        self.__token = token
        self.__vk_session = vk_api.VkApi(token=token)
        self.__vk = self.__vk_session.get_api()

    def get_current_track(self):
        """Return current user music by status"""
        user = self.__vk.users.get(users_id=self.get_vk_id(), fields="status")[0]
        if "status_audio" in user:
            status_audio = user["status_audio"]
            return status_audio
        else:
            return None

    def get_vk_id(self) -> int:
        """:return: User vk id by token"""
        response = requests.get('https://api.vk.com/method/users.get', params={
            'access_token': self.__token,
            'v': '5.131'
        })
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                user_id = data['response'][0]['id']
                return user_id


def main():
    vk = VK(token=VK_TOKEN)
    discord = Discord(discord_client_id='543726720289734656')
    while True:
        discord.update(track=vk.get_current_track())
        time.sleep(1)


if __name__ == "__main__":
    main()
