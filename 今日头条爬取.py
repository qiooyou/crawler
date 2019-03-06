import requests
from furl import furl
import io
from PIL import Image
from datetime import datetime

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

f = furl('https://www.toutiao.com/search_content/?offset=90&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20')

f.args['keyword'] = '重庆'

respone = requests.get(f.url, headers=headers)

img_url = f.scheme +':' + respone.json()['data'][0]['image_url']

f = furl(respone.json()['data'][0]['image_url'])
# f.asdict()

f.set(scheme=furl(respone.url).scheme)

f.path.segments[0] = 'large'
print(f.url)

resp = requests.get(f.url, headers=headers)
img = Image.open(io.BytesIO(resp.content))


file_base = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
## https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.save
img.save('{0}.png'.format(file_base), 'PNG')
print('{0}.png'.format(file_base))
