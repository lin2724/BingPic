import os
import sys
import json
import requests
from common_lib import LogHandle
gstLogHandler = LogHandle('bing.log')


class BingPic:
    def __init__(self):
        self.log = gstLogHandler.log
        self.m_set_store_folder = ''
        self.m_last_json_content = ''
        self.m_page_idx = 0
        self.m_set_imgs_json_url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=6&n=8'
        self.m_session_handler = requests.session()
        self.do_init()
        pass

    def do_init(self):
        self.set_store_folder('Imgs')
        set_headers = \
            {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0',
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'}
        self.m_session_handler.headers = set_headers
        pass

    def get_url_to_parse(self, last_json_content=None):
        if last_json_content is not None and last_json_content == self.m_last_json_content:
            return None
        self.m_last_json_content = last_json_content
        url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=%d&n=8' % self.m_page_idx
        self.m_page_idx += 1
        return url
        pass

    def set_store_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        self.m_set_store_folder = folder_path
        self.log('Set Store Folder to [%s]' % self.m_set_store_folder)
        pass

    def do_get(self, url):
        r = self.m_session_handler.get(url)
        if 200 != r.status_code:
            self.log('Failed get url [%s]' % url)
            return ''
        return r.content
        pass

    def parse_imgs_json(self, content):
        j = json.loads(content)
        img_dict_list = list()
        if j.has_key('images'):
            for img_info in j['images']:
                img_info_dict = dict()
                img_info_dict['url'] = 'https://cn.bing.com' + img_info['url']
                img_info_dict['urlbase'] = 'https://cn.bing.com' + img_info['urlbase']
                img_info_dict['copyright'] = img_info['copyright']
                img_dict_list.append(img_info_dict)
        else:
            self.log('Unexpected Imgs Json')
        return img_dict_list
        pass

    def download_imgs(self, img_info_dict):
        img_info_list = list()
        if type(img_info_dict) == dict:
            img_info_list.append(img_info_dict)
        else:
            img_info_list.extend(img_info_dict)
        for img_info in img_info_list:
            url = img_info['url']
            img_name = url.split('/')[-1]
            img_store_path = os.path.join(self.m_set_store_folder, img_name)
            if os.path.exists(img_store_path):
                self.log('Img Already exist [%s]' % img_store_path)
                continue
            img_content = self.do_get(url)
            if len(img_content):
                with open(img_store_path, 'wb+') as fd:
                    fd.write(img_content)
                    self.log('Download [%s]' % img_name)

    def get_img_list(self):
        json_content = None
        ret_img_dict_list = list()
        img_dict_list = list()
        while True:
            imgs_json_url = self.get_url_to_parse(json_content)
            if not imgs_json_url:
                break
            ret_img_dict_list.extend(img_dict_list)
            self.log(imgs_json_url)
            json_content = self.do_get(imgs_json_url)
            img_dict_list = self.parse_imgs_json(json_content)
        return ret_img_dict_list
        pass

    def do_parse(self):
        img_list = self.get_img_list()
        self.download_imgs(img_list)
        pass

if __name__ == '__main__':
    bing_handler = BingPic()
    bing_handler.do_parse()

