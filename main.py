import requests, json, os, re
from src.display import Ask
from src.m3u8_parser import M3U8PlaylistParser
from src.utils import get_domain, get_language, versioning_control
from models.medias import Movie, TVSerie, Url, Season, Episode
from models.tokens import Token
import argparse

DOMAIN = get_domain()
LANGUAGE = get_language()

class Search:
    def __init__(self, query) -> None:
        self.query = query
        self.result = []

    def search(self):
        api_response = requests.get(f"https://{DOMAIN}/api/search?q={self.query}").json()
        for data in api_response["data"]:
            match data["type"]:
                case "tv":
                    last_air = data["last_air_date"] if data['last_air_date'] else ''
                    self.result.append(TVSerie(title=data['name'], slug=data["slug"], internal_id=data["id"], seasons=data["seasons_count"], score=data["score"], last_air_date=last_air))
                case "movie":
                    last_air = data["last_air_date"] if data['last_air_date'] else ''
                    self.result.append(Movie(title=data['name'], slug=data["slug"], internal_id=data["id"], score=data["score"], last_air_date=last_air))

class StreamingCommunityAPI:
    def __init__(self, solution_query):
        self.domain = DOMAIN + ("/"+ LANGUAGE if LANGUAGE else "")
        self.headers = {
            'X-Inertia': 'true', 
            'X-Inertia-Version': json.loads(re.findall(r'data-page="([^"]+)"', requests.get(f"https://{self.domain}/").text)[0].replace("&quot;", '"'))["version"]
        }
        self.solution_query = solution_query
        if type(self.solution_query) == Url:
            self.content_type = 'url'
        else:
            self.content_type = 'tv' if hasattr(solution_query, 'seasons_count') else 'movie'

    def fetch_media_info(self):
        if self.content_type == 'tv':
            return self.get_serie_info()
        elif self.content_type != 'movie':
            return None 
        else:
            return None

    def get_serie_info(self) -> list:
        response = requests.get(
            f'https://{self.domain}/titles/{self.solution_query.internal_id}-{self.solution_query.slug}',
            headers=self.headers
        ).json()
        # da qua possiamo espandere e prendere un sacco di infos sulla serie. Per ora prendiamo solo le stagioni
        seasons_raw =response["props"]["title"]["seasons"]
        seasons = [Season(season["id"], season["number"], season["episodes_count"]) for season in seasons_raw]
        return seasons

    def get_season_info(self, season_index):
        headers = {'X-Inertia-Partial-Component': 'Titles/Title',  'X-Inertia-Partial-Data': 'loadedSeason'}
        response = requests.get(
            f'https://{self.domain}/titles/{self.solution_query.internal_id}-{self.solution_query.slug}/stagione-{season_index}',
            headers={**self.headers, **headers},
        )
        # da qua possiamo espandere e prendere un sacco di infos sulla stagione. Ora prendiamo solo gli episodi
        episodes_raw = response.json()["props"]["loadedSeason"]["episodes"]
        episodes = [Episode(episode["id"], episode["number"], episode["name"], episode["duration"], episode["plot"]) for episode in episodes_raw]
        return episodes


    # MARK: both return an iframe
    def get_episode_info(self, episode_id):
        response = requests.get(f'https://{self.domain}/watch/{self.solution_query.internal_id}', 
            params={'e': episode_id}, 
            headers=self.headers
        ).json()
        episode_name = f"_S{response['props']['episode']['season']['number']}E{response['props']['episode']['number']}"
        iframe_url = response["props"]["embedUrl"]
        return episode_name, iframe_url

    def get_movie_info(self):
        print(f'https://{self.domain}/watch/{self.solution_query.internal_id}')
        response = requests.get(
            f'https://{self.domain}/watch/{self.solution_query.internal_id}',
            headers=self.headers,
        ).json()
        # da qua possiamo prendere un sacco di infos sul film
        iframe_url = response["props"]["embedUrl"]
        return iframe_url

    def get_url_info(self):
        if self.solution_query.url.startswith("https://vixsrc.to"):
            return self.solution_query.url

        response = requests.get(
            self.solution_query.url,
            headers=self.headers,
        ).json()
        if embed_url := response["props"].get("embedUrl"):
            return embed_url

        internal_url = response["url"]
        response = requests.get(
            f'https://{self.domain}{internal_url}',
            headers=self.headers,
        ).json()
        iframe_url = response["props"]["embedUrl"]
        return iframe_url

    @staticmethod
    def normalize_url_to_vixsrc(url):
        if url.startswith("https://vixsrc.to"):
            return url
        
        page = requests.get(url).text
        iframe_url = re.findall(r'src="([^"]+)"', page)[0].replace("&amp;", "&")
        return iframe_url

    @staticmethod
    def get_tokens_from_iframe(url):
        url = StreamingCommunityAPI.normalize_url_to_vixsrc(url)

        iframe_source = requests.get(url).content
        iframe_video_infos = re.findall(r'<script>([\s\S]*?)<\/script>', iframe_source.decode())

        if playlist_match := re.search(r'params:\s*\{([\s\S]*?)\}\s*,', str(iframe_video_infos)):
            playlist_match_formatted = playlist_match[0].replace("\\n                \\", '').replace("\\", '').replace("n            ", '').strip()
            params_clean_matches = re.findall(r"'token[0-9a-zA-Z]*':\s*'([^']*)'", playlist_match_formatted)
            exp = re.findall(r"'expires':\s*'([^']*)'", playlist_match_formatted)[0]
            internal_url = re.findall(r"url:\s*'([^']*)',", str(iframe_video_infos).replace("\\", ''))[0]
            fhd = re.findall(r"canPlayFHD\s*true\s*\n", str(iframe_video_infos).replace("\\", '')) is not None
            filename = re.findall(r"filename\":\s*\"([^\"]*)\"", str(iframe_video_infos).replace("\\", ''))[0]
            return internal_url, Token(*params_clean_matches, fhd=fhd, expiration=exp, base_url=url), filename

    def get_media_contents(self, internal_url, tokens):
        self.master_uri = f"{internal_url}?{str(tokens)}"
        r = requests.get(self.master_uri)
        assert(r.status_code == 200)
        parser = M3U8PlaylistParser(r.text)
        parsed_data = parser()
        return parsed_data



def main():
    logo = f"""
   _____ __                            ____            __    __     
  / ___// /_________  ____ _____ ___  / __ )__  ______/ /___/ /_  __
  \__ \/ __/ ___/ _ \/ __ `/ __ `__ \/ __  / / / / __  / __  / / / /
 ___/ / /_/ /  /  __/ /_/ / / / / / / /_/ / /_/ / /_/ / /_/ / /_/ / 
/____/\__/_/   \___/\__,_/_/ /_/ /_/_____/\__,_/\__,_/\__,_/\__, / 
.{DOMAIN + " "*(58-len(DOMAIN))}/____/ 
    """
    def center(var:str, space:int=None): return '\n'.join(' ' * int(space or (os.get_terminal_size().columns - len(var.splitlines()[len(var.splitlines()) // 2])) / 2) + line for line in var.splitlines())
    print(center(logo))

    versioning_control()

    parser = argparse.ArgumentParser(prog='StreamBuddy')
    parser.add_argument('--url', '-u', required=False)
    args = parser.parse_args()
    
    if args.url is None:
        ask = Ask()
        query = ask.search_query()
        search_instance = Search(query)
        search_instance.search()

        if search_instance.result: 
            selection = ask.display_search_results(search_instance.result)
        else: print("[ERROR] Non sono stati trovati risultati per la tua ricerca")
    else:
        selection = Url(url=args.url)

    sc = StreamingCommunityAPI(selection)
    infos = sc.fetch_media_info()
    if sc.content_type == "tv":
        selected_season = ask.serie_season(infos)
        s_episodes = sc.get_season_info(selected_season)
        episode = ask.season_espisode(s_episodes)
        episode_title, iframe_url = sc.get_episode_info(episode.episode_id)
        title = f"{selection.title}_{episode_title}"
    elif sc.content_type == "movie":
        iframe_url = sc.get_movie_info()
        title = selection.title
    else:
        iframe_url = sc.get_url_info()

    internal_url, tokens, filename = sc.get_tokens_from_iframe(iframe_url)
    master_uri = f"{internal_url}?{str(tokens)}"

    print(f"yt-dlp '{master_uri}' -f 'bestvideo+bestaudio' --write-sub --sub-langs 'all' -o '{filename}'")

main()
