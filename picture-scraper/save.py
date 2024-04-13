import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO
from string import ascii_letters
from numpy.random import choice
from pathlib import Path
import sys

char = list(ascii_letters)

os.chdir(sys.argv[1])

df = pd.read_csv('id_and_pic_url.csv')

df = df.drop_duplicates('Picture')

if not os.path.isdir(os.path.join(Path(os.getcwd()), 'pictures/')):
    os.mkdir(os.path.join(Path(os.getcwd()), 'pictures/'))

os.chdir('pictures/')


def get_pic(link, name):
    if os.path.exists(name + '.jpg'):
        # Skip regeneration of existing images
        return
    try:
        print(link)
        r = requests.get(link, timeout=10)
        im = Image.open(BytesIO(r.content))
        im.save(name + '.jpg')
    except:
        print('Problem with {}'.format(link))


if __name__ == '__main__':
    print('%s started running.' % os.path.basename(__file__))
    for _, (tag, url) in df.iterrows():
        get_pic(link=url, name=tag)
    print('%s finished running.' % os.path.basename(__file__))
