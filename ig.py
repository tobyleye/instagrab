import requests
import re
import logging

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:84.0) Gecko/20100101 Firefox/84.0'}
BASE_URL = 'https://www.instagram.com/p/{}/?__a=1'


def node_extractor(node):
    __type = node['__typename']
    is_video = node['is_video']
    url = node['video_url'] if is_video else node['display_url']
    return {'__type': __type, 'is_video': is_video, 'download_url': url}


def scrape_post(shortcode):
    response = requests.get(BASE_URL.format(shortcode), headers=headers)
    print(response.text + '\n')
    logging.exception('request headers {}'.format(response.request.headers))
    print('\nwait..\n')
    logging.exception('response headers {}'.format(response.headers))
    response.raise_for_status()
    data = response.json()
    with open('debug.html', 'w') as f:
        f.write(response.text)
    parent_node = data['graphql']['shortcode_media']
    caption = parent_node['edge_media_to_caption'].get('edges', [])
    if len(caption) > 0:
        caption = caption[0]['node']['text']
    else:
        caption = ''
    children_node = parent_node.get('edge_sidecar_to_children')
    owner = {'username': parent_node['owner']['username'],
            'full_name': parent_node['owner']['full_name'],
            'avatar': parent_node['owner']['profile_pic_url'],
        }

    if parent_node['__typename'] == 'GraphSidecar' and children_node:
        posts = [node_extractor(edge['node']) 
                    for edge in children_node['edges']]
    else:
        posts = [node_extractor(parent_node)]
    return {'posts': posts, 'owner': owner, 'caption': caption}

def extract_shortcode_from_url(url):
    match=re.search('instagram.com/p/([^/?]*)', url)
    if match:
        return match.group(1).strip('/')

def run(url):
    shortcode=extract_shortcode_from_url(url)
    if shortcode:
        return scrape_post(shortcode)

if __name__ == "__main__":
    import sys
    import pprint
    if len(sys.argv) > 1:
        url=sys.argv[1]
        pprint.pprint(run(url))
    else:
        print('wrong use of script')
        sys.exit(0)
