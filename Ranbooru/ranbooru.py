import requests
import random
from typing import Literal
import os

POST_AMOUNT = 100

class Booru():
    
    def __init__(self, booru, booru_url):
        self.booru = booru
        self.booru_url = booru_url
        self.headers = {'user-agent': 'my-app/0.0.1'}
        
    def get_data(self,add_tags,max_pages=10, id=''):
        pass
    
    def get_post(self,add_tags,max_pages=10, id=''):
        pass
    
class Gelbooru(Booru):
    
    def __init__(self, fringe_benefits=True):
        super().__init__('gelbooru', f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={POST_AMOUNT}')
        self.fringeBenefits = fringe_benefits

    def get_data(self, add_tags, max_pages=10, id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&pid={random.randint(0,max_pages)}{id}{add_tags}"
        if self.fringeBenefits:
            res = requests.get(self.booru_url, cookies={'fringeBenefits': 'yup'})
        else:
            res = requests.get(self.booru_url)
        data = res.json()
        return data
    
    def get_post(self, add_tags, max_pages=10, id=''):
        return self.get_data(add_tags, max_pages, "&id="+id)
    
    
class XBooru(Booru):
    
    def __init__(self):
        super().__init__('xbooru', f'https://xbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10, id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&pid={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url)
        data = res.json()
        for post in data:
            post['file_url'] = f"https://xbooru.com/images/{post['directory']}/{post['image']}"
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        return self.get_data(add_tags, max_pages, "&id="+id)
    
class Rule34(Booru):
    
    def __init__(self):
        super().__init__('rule34', f'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10,id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&pid={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url)
        data = res.json()
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        return self.get_data(add_tags, max_pages, "&id="+id)
    
class Safebooru(Booru):
    
    def __init__(self):
        super().__init__('safebooru', f'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10,id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&pid={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url)
        data = res.json()
        for post in data:
            post['file_url'] = f"https://safebooru.org/images/{post['directory']}/{post['image']}"
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        return self.get_data(add_tags, max_pages, "&id="+id)
    
class Konachan(Booru):
    
    def __init__(self):
        super().__init__('konachan', f'https://konachan.com/post.json?limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10,id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&page={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url)
        data = res.json()
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        raise Exception("Konachan does not support post IDs")
    
class Yandere(Booru):
    
    def __init__(self):
        super().__init__('yande.re', f'https://yande.re/post.json?limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10,id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&page={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url)
        data = res.json()
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        raise Exception("Yande.re does not support post IDs")
    
class AIBooru(Booru):
    
    def __init__(self):
        super().__init__('AIBooru', f'https://aibooru.online/posts.json?limit={POST_AMOUNT}')
                
    def get_data(self, add_tags, max_pages=10,id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&page={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url)
        data = res.json()
        for post in data:
            post['tags'] = post['tag_string']
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        raise Exception("AIBooru does not support post IDs")
    
class Danbooru(Booru):
    
    def __init__(self):
        super().__init__('danbooru', f'https://danbooru.donmai.us/posts.json?limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10, id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&page={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url, headers=self.headers)
        data = res.json()
        for post in data:
            post['tags'] = post['tag_string']
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        self.booru_url = f"https://danbooru.donmai.us/posts/{id}.json"
        res = requests.get(self.booru_url, headers=self.headers)
        data = res.json()
        data['tags'] = data['tag_string']
        data = {'post': [data]}
        return data
    
class e621(Booru):
    
    def __init__(self):
        super().__init__('danbooru', f'https://e621.net/posts.json?limit={POST_AMOUNT}')
        
    def get_data(self, add_tags, max_pages=10, id=''):
        if id:
            add_tags = ''
        self.booru_url = f"{self.booru_url}&page={random.randint(0,max_pages)}{id}{add_tags}"
        res = requests.get(self.booru_url, headers=self.headers)
        data = res.json()['posts']
        for post in data:
            temp_tags = []
            sublevels = ['general','artist','copyright','character','species']
            for sublevel in sublevels:
                temp_tags.extend(post['tags'][sublevel])
            post['tags'] = ' '.join(temp_tags)
            post['score'] = post['score']['total']
        return {'post': data}
    
    def get_post(self, add_tags, max_pages=10, id=''):
        self.get_data(add_tags, max_pages, "&id="+id)

BOORUS = ['gelbooru', 'rule34', 'safebooru', 'danbooru', 'konachan', 'yande.re', 'aibooru', 'xbooru', 'e621']
COLORED_BG = ['black_background','aqua_background','white_background','colored_background','gray_background','blue_background','green_background','red_background','brown_background','purple_background','yellow_background','orange_background','pink_background','plain','transparent_background','simple_background','two-tone_background','grey_background']
BW_BG = ['monochrome','greyscale','grayscale']

RATING_TYPES = {
    "none": {
        "All": "All"
    },
    "full": {
        "All": "All",
        "Safe": "safe",
        "Questionable": "questionable",
        "Explicit": "explicit"
    },
    "single": {
        "All": "All",
        "Safe": "g",
        "Sensitive": "s",
        "Questionable": "q",
        "Explicit": "e"
    }
}
RATINGS = {
    "e621": RATING_TYPES['full'],
    "danbooru": RATING_TYPES['single'],
    "aibooru": RATING_TYPES['full'],
    "yande.re": RATING_TYPES['full'],
    "konachan": RATING_TYPES['full'],
    "safebooru": RATING_TYPES['none'],
    "rule34": RATING_TYPES['full'],
    "xbooru": RATING_TYPES['full'],
    "gelbooru": RATING_TYPES['single']
}

class Ranbooru:    
    def __init__(self):
        self.last_prompt = ''

    @classmethod
    def INPUT_TYPES(cls):
               
        return {"required": {       
                    "booru": (BOORUS, {"default": "gelbooru"}),
                    "tags": ("STRING", {"multiline": False, "default": ""}),
                    "remove_tags": ("STRING", {"multiline": False, "default": ""}),
                    "max_tags": ("INT", {"default": 100, "min": 1, "max": 100}),
                    "rating": (["All","Safe","Questionable","Explicit"], {"default": "All"}),
                    "change_color": (["Default","Colored","Limited Palette","Monochrome"], {"default": "Default"}),
                    "use_last_prompt": (["True","False"], {"default": "True"})
                    }
                }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "ranbooru"
    CATEGORY = "Ranbooru Nodes"
    
    def IS_CHANGED(self, **kwargs):
        return float('nan')

    def ranbooru(self, booru, tags, remove_tags, max_tags, rating, change_color, use_last_prompt):

        booru_apis = {
                'gelbooru': Gelbooru(),
                'rule34': Rule34(),
                'safebooru': Safebooru(),
                'danbooru': Danbooru(),
                'konachan': Konachan(),
                'yande.re': Yandere(),
                'aibooru': AIBooru(),
                'xbooru': XBooru(),
                'e621': e621(),
            }
        bad_tags = ['mixed-language_text','watermark','text','english_text','speech_bubble','signature','artist_name','censored','bar_censor','translation','twitter_username',"twitter_logo",'patreon_username','commentary_request','tagme','commentary','character_name','mosaic_censoring','instagram_username','text_focus','english_commentary','comic','translation_request','fake_text','translated','paid_reward_available','thought_bubble','multiple_views','silent_comic','out-of-frame_censoring','symbol-only_commentary','3koma','2koma','character_watermark','spoken_question_mark','japanese_text','spanish_text','language_text','fanbox_username','commission','original','ai_generated','stable_diffusion','tagme_(artist)','text_bubble','qr_code','chinese_commentary','korean_text','partial_commentary','chinese_text','copyright_request','heart_censor','censored_nipples','page_number','scan','fake_magazine_cover','korean_commentary']
        if ',' in remove_tags:
            bad_tags.extend(remove_tags.split(','))
        else:
            bad_tags.append(remove_tags)
        
        api_url = ''
        random_post = {'preview_url':''}
        data = {'post': [{'tags': ''}]}
        if use_last_prompt == 'True' and self.last_prompt != '':
            final_tags = self.last_prompt
        else:
            api_url = booru_apis.get(booru, Gelbooru())
            
            add_tags = ''
            if tags != '':
                add_tags = f'&tags=-animated+{tags.replace(",", "+")}'
            else:
                add_tags = '&tags=-animated'
            if rating != 'All':
                add_tags += f'+rating:{RATINGS[booru][rating]}'

            data = api_url.get_data(add_tags, 100)
            random_post = data['post'][random.randint(0,len(data['post'])-1)]
            clean_tags = random_post['tags'].replace('(','\(').replace(')','\)')
            temp_tags = clean_tags.split(' ')
            temp_tags = random.sample(temp_tags, len(temp_tags))
            if max_tags > 0:
                temp_tags = temp_tags[:max_tags]
            if change_color == 'Colored':
                bad_tags.extend(BW_BG)
            elif change_color == 'Limited Palette':
                temp_tags.append('(limited_palette:1.3)')
            elif change_color == 'Monochrome':
                temp_tags.extend(BW_BG)
            final_tags = ','.join([tag for tag in temp_tags if tag not in bad_tags])
            for bad_tag in bad_tags:
                if '*' in bad_tag:
                    final_tags = ','.join([tag for tag in final_tags.split(',') if bad_tag.replace('*','') not in tag])  
            self.last_prompt = final_tags
        
        return (final_tags,)        
    
class RandomPicturePath:
    # given a path, return a random picture (png,jpg,jpeg) from that path as a string
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                    "path": ("STRING", {"multiline": False, "default": ""}),
                    "parse_subfolders": (["True","False"], {"default": "True"}),
                    }
                }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "random_picture_path"
    CATEGORY = "Ranbooru Nodes"
    
    def IS_CHANGED(self, **kwargs):
        return float('nan')
    
    def random_picture_path(self, path, parse_subfolders):
        files = []
        if parse_subfolders == 'True':
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        files.append(os.path.join(root, filename))
        else:
            files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(('.png', '.jpg', '.jpeg'))]
        
        return (random.choice(files),)
    
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Ranbooru": Ranbooru,
    "RandomPicturePath": RandomPicturePath
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "Ranbooru": "Ranbooru",
    "RandomPicturePath": "Random Picture Path"
}
