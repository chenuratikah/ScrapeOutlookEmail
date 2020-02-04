import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import shutil


class scrapeimg:
    def __init__(self, url):
        self.url = url

    def getImage(self):

        resp = requests.get(self.url, stream=True)
        # Open a local file with wb ( write binary ) permission.
        local_file = open(r'D:\local_image.png', 'wb')
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        resp.raw.decode_content = True
        # Copy the response stream raw data to local image file.
        shutil.copyfileobj(resp.raw, local_file)
        # Remove the image url response object.
        del resp
    