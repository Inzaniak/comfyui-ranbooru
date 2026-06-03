import datetime
import requests
import random
from typing import Literal
import os
import torch
import numpy as np
from PIL import Image
import io
import re
import configparser
from pathlib import Path

# Find the local folder and set the filename for the config file.
cpath = Path(__file__).parent.resolve()
conffile = cpath / "ranbooru.conf"

#Define the config parser process
rbconf = configparser.ConfigParser()

# check for the file and create if missing
if conffile.exists():
    print("Ranbooru: Conf file found!")
else:  
    rbconf['DEFAULT'] = { 'gelbooru_id': '',
                          'gelbooru_key': '',
                          'rule34_id': '',
                          'rule34_key': '',
                          'safebooru_id': '',
                          'safebooru_key': '',
                          'danbooru_id': '',
                          'danbooru_key': '',
                          'konachan_id': '',
                          'konachan_key': '',
                          'yande.re_id': '',
                          'yande.re_key': '',
                          'aibooru_id': '',
                          'aibooru_key': '',
                          'xbooru_id': '',
                          'xbooru_key': '',
                          'e621_id': '',
                          'e621_key': ''}
    rbconf['UserKeys'] = {}
    with open(conffile, 'w') as configfile:
        rbconf.write(configfile)
    print ("Ranbooru: Conf file created. Please update with your API information!")

#Read the config file in and set the group
rbconf.read(conffile)
userkeys = rbconf['UserKeys']

#Start a http requests session and set the user-agent string
sess = requests.Session()
head_string = {"user-agent": "comfyui-ranbooru/0.0.0"}
sess.headers.update(head_string)

# define a function to create a random number based on the seed value
def random_num(min, max, seed):
    random.seed(seed)
    return random.randint(min, max)

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

class Booru():
    def __init__(self, booru, booru_url):
        self.booru = booru
        self.booru_url = booru_url

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        pass

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        pass

class Gelbooru(Booru):
    def __init__(self, fringe_benefits=True):
        APIKEY=userkeys.get('gelbooru_key', '')
        APIID=userkeys.get('gelbooru_id', '')
        super().__init__(
            "gelbooru",
            f"https://gelbooru.com/index.php?api_key={APIKEY}&user_id={APIID}&page=dapi&s=post&q=index&json=1",
        )
        self.fringeBenefits = fringe_benefits

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""

        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&pid={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        if self.fringeBenefits:
            res = sess.get(self.booru_url, cookies={"fringeBenefits": "yup"})
        else:
            res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        return data

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        return self.get_data(add_tags, max_pages, posts_per_page, 0, seed, "&id=" + id, api_key)

class XBooru(Booru):
    def __init__(self):
        APIKEY=userkeys.get('xbooru_key', '')
        APIID=userkeys.get('xbooru_id', '')
        super().__init__(
            "xbooru",
            f"https://xbooru.com/index.php?api_key={APIKEY}&user_id={APIID}&page=dapi&s=post&q=index&json=1",
        )

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&pid={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        for post in data:
            post["file_url"] = (
                f"https://xbooru.com/images/{post['directory']}/{post['image']}"
            )
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        return self.get_data(add_tags, max_pages, posts_per_page, 0, seed, "&id=" + id, api_key)

class Rule34(Booru):
    def __init__(self):
        APIKEY=userkeys.get('rule34_key', '')
        APIID=userkeys.get('rule34_id', '')
        super().__init__(
            "rule34",
            f"https://api.rule34.xxx/index.php?api_key={APIKEY}&user_id={APIID}&page=dapi&s=post&q=index&json=1",
        )

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&pid={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        return self.get_data(add_tags, max_pages, posts_per_page, 0, seed, "&id=" + id, api_key)

class Safebooru(Booru):
    def __init__(self):
        APIKEY=userkeys.get('safebooru_key', '')
        APIID=userkeys.get('safebooru_id', '')
        super().__init__(
            "safebooru",
            f"https://safebooru.org/index.php?api_key={APIKEY}&user_id={APIID}&page=dapi&s=post&q=index&json=1",
        )

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&pid={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url) 

        if api_key:
            self.booru_url += api_key
       
        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        for post in data:
            post["file_url"] = (
                f"https://safebooru.org/images/{post['directory']}/{post['image']}"
            )
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        return self.get_data(add_tags, max_pages, posts_per_page, 0, seed, "&id=" + id, api_key)

class Konachan(Booru):
    def __init__(self):
        APIKEY=userkeys.get('konachan_key', '')
        APIID=userkeys.get('konochan_id', '')
        super().__init__(
            "konachan", f"https://konachan.com/post.json?api_key={APIKEY}&user_id={APIID}"
        )

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&page={rpage}{id}{add_tags}"
        )
        
        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        raise Exception("Konachan does not support post IDs")

class Yandere(Booru):
    def __init__(self):
        APIKEY=userkeys.get('yande.re_key', '')
        APIID=userkeys.get('yande.re_id', '')
        super().__init__("yande.re", f"https://yande.re/post.json?api_key={APIKEY}&user_id={APIID}")

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&page={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        raise Exception("Yande.re does not support post IDs")

class AIBooru(Booru):
    def __init__(self):
        APIKEY=userkeys.get('aibooru_key', '')
        APIID=userkeys.get('aibooru_id', '')
        super().__init__(
            "AIBooru", f"https://aibooru.online/posts.json?api_key={APIKEY}&login={APIID}"
        )

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&page={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        for post in data:
            post["tags"] = post["tag_string"]
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        raise Exception("AIBooru does not support post IDs")

class Danbooru(Booru):
    def __init__(self):
        APIKEY=userkeys.get('danbooru_key', '')
        APIID=userkeys.get('danbooru_id', '')
        super().__init__(
            "danbooru", f"https://danbooru.donmai.us/posts.json?api_key={APIKEY}&login={APIID}"
        )

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&page={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        for post in data:
            post["tags"] = post["tag_string"]
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        self.booru_url = f"https://danbooru.donmai.us/posts/{id}.json"
        if api_key:
            self.booru_url += api_key
        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        data["tags"] = data["tag_string"]
        data = {"post": [data]}
        return data

class e621(Booru):
    def __init__(self):
        APIKEY=userkeys.get('e621_key', '')
        APIID=userkeys.get('e621_id', '')
        super().__init__("danbooru", f"https://e621.net/posts.json?api_key={APIKEY}&login={APIID}")

    def get_data(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        if id:
            add_tags = ""
        self.booru_url = (
            f"{self.booru_url}&limit={posts_per_page}&page={rpage}{id}{add_tags}"
        )

        # Troubleshooting line to check the URL being requested
        #print(self.booru_url)

        if api_key:
            self.booru_url += api_key

        res = sess.get(self.booru_url)
        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            print(f"[Ranbooru] API request failed!")
            print(f"[Ranbooru] URL: {self.booru_url}")
            print(f"[Ranbooru] HTTP Status: {res.status_code}")
            print(f"[Ranbooru] Response: {res.text[:500]}")
            raise Exception(f"Booru API returned invalid response (HTTP {res.status_code}). Check console for response details.")
        data = data["posts"]
        for post in data:
            temp_tags = []
            sublevels = ["general", "artist", "copyright", "character", "species"]
            for sublevel in sublevels:
                temp_tags.extend(post["tags"][sublevel])
            post["tags"] = " ".join(temp_tags)
            post["score"] = post["score"]["total"]
            post["file_url"] = post["file"]["url"]
        return {"post": data}

    def get_post(self, add_tags, max_pages, posts_per_page, rpage, seed, id="", api_key=""):
        self.get_data(add_tags, max_pages, posts_per_page, 0, seed, "&id=" + id, api_key)

BOORUS = [
    "gelbooru",
    "rule34",
    "safebooru",
    "danbooru",
    "konachan",
    "yande.re",
    "aibooru",
    "xbooru",
    "e621",
]
BOORUS_URL = ["gelbooru", "rule34", "safebooru", "yande.re", "aibooru", "xbooru"]
COLORED_BG = [
    "black_background",
    "aqua_background",
    "white_background",
    "colored_background",
    "gray_background",
    "blue_background",
    "green_background",
    "red_background",
    "brown_background",
    "purple_background",
    "yellow_background",
    "orange_background",
    "pink_background",
    "plain",
    "transparent_background",
    "simple_background",
    "two-tone_background",
    "grey_background",
]
BW_BG = ["monochrome", "greyscale", "grayscale"]

RATING_TYPES = {
    "none": {"All": "All"},
    "full": {
        "All": "All",
        "Safe": "safe",
        "Sensitive": "questionable",
        "Questionable": "questionable",
        "Explicit": "explicit",
    },
    "single": {
        "All": "All",
        "Safe": "g",
        "Sensitive": "s",
        "Questionable": "q",
        "Explicit": "e",
    },
}
RATINGS = {
    "e621": RATING_TYPES["full"],
    "danbooru": RATING_TYPES["single"],
    "aibooru": RATING_TYPES["full"],
    "yande.re": RATING_TYPES["full"],
    "konachan": RATING_TYPES["full"],
    "safebooru": RATING_TYPES["none"],
    "rule34": RATING_TYPES["full"],
    "xbooru": RATING_TYPES["full"],
    "gelbooru": RATING_TYPES["single"],
}

class Ranbooru:
    def __init__(self):
        self.last_prompt = ""
        self.file_url = ""
        self.image = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "booru": (BOORUS, {"default": "gelbooru"}),
                "max_pages": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 100,
                        "step": 1,
                        "display": "number",
                    },
                ),
                "posts_per_page": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 100,
                        "step": 1,
                        "display": "number",
                    },
                ),
		"seed": (
                    "INT",
                    {
                         "default": 0,
                         "min": 0, 
                         "max": 0xffffffffffffffff
                     }
                ),
                "tags": ("STRING", {"multiline": False, "default": ""}),
                "rating": (
                    ["All", "Safe", "Sensitive", "Questionable", "Explicit"],
                    {"default": "All"},
                ),
                "change_color": (
                    ["Default", "Colored", "Limited Palette", "Monochrome"],
                    {"default": "Default"},
                ),
                "use_last_prompt": ("BOOLEAN", {"default": False}),
                "return_picture": ("BOOLEAN", {"default": False}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "IMAGE",
        "STRING",
    )
    RETURN_NAMES = (
        "TAGS",
        "IMAGE",
        "IMAGE_URL",
    )
    FUNCTION = "ranbooru"
    CATEGORY = "Ranbooru Nodes"

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("nan")

    def ranbooru(
        self,
        booru,
        max_pages,
        posts_per_page,
        seed,
        tags,
        rating,
        change_color,
        use_last_prompt,
        return_picture,
        api_key,
    ):
        if not api_key:
            raise Exception("api_key is required. The booru API now requires an API key. Please paste your key in the api_key field.")
        booru_apis = {
            "gelbooru": Gelbooru(),
            "rule34": Rule34(),
            "safebooru": Safebooru(),
            "danbooru": Danbooru(),
            "konachan": Konachan(),
            "yande.re": Yandere(),
            "aibooru": AIBooru(),
            "xbooru": XBooru(),
            "e621": e621(),
        }
        bad_tags = [
            "mixed-language_text",
            "watermark",
            "text",
            "english_text",
            "speech_bubble",
            "signature",
            "artist_name",
            "censored",
            "bar_censor",
            "translation",
            "twitter_username",
            "twitter_logo",
            "patreon_username",
            "commentary_request",
            "tagme",
            "commentary",
            "character_name",
            "mosaic_censoring",
            "instagram_username",
            "text_focus",
            "english_commentary",
            "comic",
            "translation_request",
            "fake_text",
            "translated",
            "paid_reward_available",
            "thought_bubble",
            "multiple_views",
            "silent_comic",
            "out-of-frame_censoring",
            "symbol-only_commentary",
            "3koma",
            "2koma",
            "character_watermark",
            "spoken_question_mark",
            "japanese_text",
            "spanish_text",
            "language_text",
            "fanbox_username",
            "commission",
            "original",
            "ai_generated",
            "stable_diffusion",
            "tagme_(artist)",
            "text_bubble",
            "qr_code",
            "chinese_commentary",
            "korean_text",
            "partial_commentary",
            "chinese_text",
            "copyright_request",
            "heart_censor",
            "censored_nipples",
            "page_number",
            "scan",
            "fake_magazine_cover",
            "korean_commentary",
        ]

        api_url = ""
        random_post = {"preview_url": ""}
        data = {"post": [{"tags": ""}]}
        cached = use_last_prompt and self.last_prompt != ""
        if cached:
            final_tags = self.last_prompt
            img_url = self.file_url
        else:
            api_url = booru_apis.get(booru, Gelbooru())

            add_tags = ""
            if tags != "":
                add_tags = f'&tags=-animated+{tags.replace(",", "+")}'
            else:
                add_tags = "&tags=-animated"
            if rating != "All":
                add_tags += f"+rating:{RATINGS[booru][rating]}"
            
            #Using the max page setting and seed, pull a random page
            rpage = random_num(0, max_pages, seed)
            data = api_url.get_data(add_tags, max_pages, posts_per_page, rpage, seed, api_key=api_key)
            rpost = random_num(0, len(data["post"]) - 1, seed)

            random_post = data["post"][rpost]
            clean_tags = random_post["tags"].replace("(", "\\(").replace(")", "\\)")
            temp_tags = clean_tags.split(" ")
            temp_tags = random.sample(temp_tags, len(temp_tags))
            if change_color == "Colored":
                bad_tags.extend(BW_BG)
            elif change_color == "Limited Palette":
                temp_tags.append("(limited_palette:1.3)")
            elif change_color == "Monochrome":
                temp_tags.extend(BW_BG)
            final_tags = ",".join([tag for tag in temp_tags if tag not in bad_tags])
            self.last_prompt = final_tags
            self.file_url = random_post["file_url"]

            #Print the referencing and image URL to console for logging/reference
            print(api_url.booru_url)
            print(self.file_url)

        if return_picture:
            if cached:
                if self.file_url == img_url and self.image != None:
                    img = self.image
            else:
                img_url = random_post["file_url"]
                res = sess.get(img_url, headers={'referer': api_url.booru_url})
                #Log Errors to console
                if res.status_code != 200:
                	print(f"Error in image download: HTTP Code {res.status_code}")
                else:
                        # read the image in PIL
                        img = Image.open(io.BytesIO(res.content))
                        # rgb
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        self.file_url = img_url
                        self.image = img
            return (
                final_tags,
                pil2tensor(img),
                self.file_url,
            )
        else:
            empty_image = Image.new("RGB", (1, 1), color=(0, 0, 0))
            return (
                final_tags,
                pil2tensor(empty_image),
                self.file_url,
            )

class RanbooruURL:
    """Uses an url or an ID to get a post from a booru"""

    def __init__(self):
        self.last_prompt = ""
        self.file_url = ""
        self.image = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "booru": (BOORUS_URL, {"default": "gelbooru"}),
                "url": ("STRING", {"multiline": False, "default": ""}),
                "return_picture": ("BOOLEAN", {"default": False}),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "IMAGE",
        "STRING",
    )
    RETURN_NAMES = (
        "TAGS",
        "IMAGE",
        "IMAGE_URL",
    )
    FUNCTION = "ranbooru_url"
    CATEGORY = "Ranbooru Nodes"

    def ranbooru_url(self, booru, url, return_picture, api_key):
        if not api_key:
            raise Exception("api_key is required. The booru API now requires an API key. Please paste your key in the api_key field.")
        booru_apis = {
            "gelbooru": Gelbooru(),
            "rule34": Rule34(),
            "safebooru": Safebooru(),
            "yande.re": Yandere(),
            "aibooru": AIBooru(),
            "xbooru": XBooru(),
        }

        bad_tags = [
            "mixed-language_text",
            "watermark",
            "text",
            "english_text",
            "speech_bubble",
            "signature",
            "artist_name",
            "censored",
            "bar_censor",
            "translation",
            "twitter_username",
            "twitter_logo",
            "patreon_username",
            "commentary_request",
            "tagme",
            "commentary",
            "character_name",
            "mosaic_censoring",
            "instagram_username",
            "text_focus",
            "english_commentary",
            "comic",
            "translation_request",
            "fake_text",
            "translated",
            "paid_reward_available",
            "thought_bubble",
            "multiple_views",
            "silent_comic",
            "out-of-frame_censoring",
            "symbol-only_commentary",
            "3koma",
            "2koma",
            "character_watermark",
            "spoken_question_mark",
            "japanese_text",
            "spanish_text",
            "language_text",
            "fanbox_username",
            "commission",
            "original",
            "ai_generated",
            "stable_diffusion",
            "tagme_(artist)",
            "text_bubble",
            "qr_code",
            "chinese_commentary",
            "korean_text",
            "partial_commentary",
            "chinese_text",
            "copyright_request",
            "heart_censor",
            "censored_nipples",
            "page_number",
            "scan",
            "fake_magazine_cover",
            "korean_commentary",
        ]

        api_url = ""
        random_post = {"preview_url": ""}
        data = {"post": [{"tags": ""}]}
        api_url = booru_apis.get(booru, Gelbooru())

        # check if the id is a number otherwise it's an url
        if url.isdigit():
            add_tags = f"&id={url}"
        else:
            # extract the id from the url
            # use regex to find the number after id=
            id = re.search(r"id=(\d+)", url)
            if id:
                add_tags = f"&id={id.group(1)}"
            else:
                raise Exception("Invalid URL")

        data = api_url.get_data(add_tags, 100, 100, 0, 0, api_key=api_key)
        random_post = data["post"][0]
        clean_tags = random_post["tags"].replace("(", "\\(").replace(")", "\\)")
        temp_tags = clean_tags.split(" ")
        temp_tags = random.sample(temp_tags, len(temp_tags))
        final_tags = ",".join([tag for tag in temp_tags if tag not in bad_tags])
        self.last_prompt = final_tags
        self.file_url = random_post["file_url"]

        if return_picture:
            img_url = random_post["file_url"]
            res = sess.get(img_url, headers={'referer': api_url.booru_url})
            # read the image in PIL
            img = Image.open(io.BytesIO(res.content))
            # rgb
            if img.mode != "RGB":
                img = img.convert("RGB")
            self.file_url = img_url
            self.image = img
            return (
                final_tags,
                pil2tensor(img),
                self.file_url,
            )
        else:
            empty_image = Image.new("RGB", (1, 1), color=(0, 0, 0))
            return (
                final_tags,
                pil2tensor(empty_image),
                self.file_url,
            )

class PromptRemove:
    # given a prompt, split it by separator and remove the words in the list based on the input list separated by comma
    # if the word in the list contains a * then it will remove all the words that contain that word
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {}),
                "separator": ("STRING", {"default": ","}),
                "remove_tags": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "prompt_remove"
    CATEGORY = "Ranbooru Nodes"

    def prompt_remove(self, prompt, separator, remove_tags):
        tags = prompt.split(separator)
        if "," in remove_tags:
            remove_tags = remove_tags.split(",")
        else:
            remove_tags = [remove_tags]
        for bad_tag in remove_tags:
            if "*" in bad_tag:
                tags = [tag for tag in tags if bad_tag.replace("*", "") not in tag]
            else:
                tags = [tag for tag in tags if tag != bad_tag]
        return (separator.join(tags),)

class RandomPicturePath:
    # given a path, return a random picture (png,jpg,jpeg) from that path as a string
    def __init__(self):
        self.last_path = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"multiline": False, "default": ""}),
                "parse_subfolders": (["True", "False"], {"default": "True"}),
                "use_last": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "random_picture_path"
    CATEGORY = "Ranbooru Nodes"

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("nan")

    def random_picture_path(self, path, parse_subfolders, use_last):
        if use_last and self.last_path != "":
            return (self.last_path,)
        else:
            files = []
            if parse_subfolders == "True":
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        if filename.endswith((".png", ".jpg", ".jpeg")):
                            files.append(os.path.join(root, filename))
            else:
                files = [
                    os.path.join(path, file)
                    for file in os.listdir(path)
                    if file.endswith((".png", ".jpg", ".jpeg"))
                ]
            random_file = random.choice(files)
            self.last_path = random_file
            return (random_file,)

class PromptMix:
    def __init__(self):
        self.last_prompt = ""

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("nan")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": False, "default": ""}),
                "delimiter": ("STRING", {"multiline": False, "default": ","}),
                "mix_type": (["Off", "Mix", "Inverse"], {"default": "Off"}),
                "use_last": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "prompt_mix"
    CATEGORY = "Ranbooru Nodes"

    def prompt_mix(self, prompt, delimiter, mix_type, use_last):
        """Split the string by delimiter and mixes the order of the words"""
        if use_last and self.last_prompt != "":
            return (self.last_prompt,)
        else:
            words = prompt.split(delimiter)
            if mix_type == "Mix":
                random.shuffle(words)
            elif mix_type == "Inverse":
                words.reverse()
            self.last_prompt = delimiter.join(words)
            return (self.last_prompt,)

class PromptLimit:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {}),
                "separator": ("STRING", {"default": ","}),
                "limit": ("INT", {"default": 0, "min": 0, "max": 100}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "prompt_limit"
    CATEGORY = "Ranbooru Nodes"

    def prompt_limit(self, prompt, separator, limit):
        """Split the string by separator and limit the amount of words"""
        words = prompt.split(separator)
        if limit > 0:
            words = words[:limit]
        return (separator.join(words),)

class PromptRandomWeight:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {}),
                "separator": ("STRING", {"default": ","}),
                "min_weight_value": (
                    "FLOAT",
                    {"default": 0.0, "min": -5.0, "max": 5.0},
                ),
                "max_weight_value": (
                    "FLOAT",
                    {"default": 1.0, "min": -5.0, "max": 5.0},
                ),
                "max_weight_tags": ("INT", {"default": 1, "min": 1, "max": 100}),
                "order": (["Random", "Ordered"], {"default": "Random"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "prompt_random_weight"
    CATEGORY = "Ranbooru Nodes"

    def prompt_random_weight(
        self,
        prompt,
        separator,
        min_weight_value,
        max_weight_value,
        max_weight_tags,
        order,
    ):
        """Split the string by separator and randomly add (word:weight) to tags contained in the list based on the max_weight_value to a max of max_weight_tags
        If the weight is above 1 than the value should be between 1 and max_weight_value, otherwise it should be between max_weight_value and 1
        Check if the max_weight_tags is less than the amount of words in the prompt
        """
        words = prompt.split(separator)
        if max_weight_tags > len(words):
            max_weight_tags = len(words)
        if order == "Random":
            # apply weights to random words in the list
            # these should not be always the first words
            random_words = random.sample(
                [word for word in words if "(" not in word], max_weight_tags
            )
            for i in range(max_weight_tags):
                words[words.index(random_words[i])] = (
                    f"({words[words.index(random_words[i])]}:{round(random.uniform(min_weight_value,max_weight_value),1)})"
                )
        else:
            for i in range(max_weight_tags):
                words[i] = (
                    f"({words[i]}:{round(random.uniform(min_weight_value,max_weight_value),1)})"
                )
        return (separator.join(words),)

class PromptBackground:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {}),
                "background_type": (
                    ["colored", "b&w", "remove"],
                    {"default": "remove"},
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "prompt_background"
    CATEGORY = "Ranbooru Nodes"

    def prompt_background(self, prompt, background_type):
        COLORED_BG = [
            "black_background",
            "aqua_background",
            "white_background",
            "colored_background",
            "blue_background",
            "green_background",
            "red_background",
            "brown_background",
            "purple_background",
            "yellow_background",
            "orange_background",
            "pink_background",
            "two-tone_background",
            "grey_background",
        ]
        BW_BG = ["monochrome", "greyscale", "grayscale"]

        # Merge all background tags
        ALL_BG_TAGS = COLORED_BG + BW_BG

        # Split prompt in tags
        tags = prompt.split(",")

        if background_type == "remove":
            # Remove all background tags
            tags = [tag.strip() for tag in tags if tag.strip() not in ALL_BG_TAGS]
        elif background_type == "colored":
            # Remove all black and white tags
            tags = [tag.strip() for tag in tags if tag.strip() not in BW_BG]
            # Add a random colored background tag
            tags.append(random.choice(COLORED_BG))
        elif background_type == "b&w":
            # Remove all colored tags
            tags = [tag.strip() for tag in tags if tag.strip() not in COLORED_BG]
            # Add all black and white tags
            tags.extend(BW_BG)

        # Ricomponi i tag nel prompt
        final_prompt = ", ".join(tags)

        return (final_prompt,)

class LockSeed:
    """Returns a random seed and stores it in self.prev_seed. If user selects 'use_last' it will return the same seed as before."""

    def __init__(self):
        self.prev_seed = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "use_last": ("BOOLEAN", {"default": False}),
            }
        }

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("nan")

    RETURN_TYPES = ("INT",)
    FUNCTION = "lock_seed"
    CATEGORY = "Ranbooru Nodes"

    def lock_seed(self, use_last):
        if use_last and self.prev_seed != None:
            return (self.prev_seed,)
        else:
            seed = random.randint(0, 1000000000)
            self.prev_seed = seed
            return (seed,)

class TimestampFileName:
    """Given a filename input, returns a filename with a timestamp appended to it."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filename": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("nan")

    RETURN_TYPES = ("STRING",)
    FUNCTION = "timestamp_filename"
    CATEGORY = "Ranbooru Nodes"

    def timestamp_filename(self, filename):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return (f"{filename}_{timestamp}",)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Ranbooru": Ranbooru,
    "RandomPicturePath": RandomPicturePath,
    "PromptMix": PromptMix,
    "PromptLimit": PromptLimit,
    "PromptRandomWeight": PromptRandomWeight,
    "PromptBackground": PromptBackground,
    "PromptRemove": PromptRemove,
    "RanbooruURL": RanbooruURL,
    "LockSeed": LockSeed,
    "TimestampFileName": TimestampFileName,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "Ranbooru": "Ranbooru",
    "RandomPicturePath": "Random Picture Path",
    "PromptMix": "Prompt Mix",
    "PromptLimit": "Prompt Limit",
    "PromptRandomWeight": "Prompt Random Weight",
    "PromptBackground": "Prompt Background",
    "PromptRemove": "Prompt Remove",
    "RanbooruURL": "Ranbooru URL",
    "LockSeed": "Lock Seed",
    "TimestampFileName": "Timestamp Filename",
}
