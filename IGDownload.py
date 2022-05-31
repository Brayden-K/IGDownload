import requests, random, string, time, os, threading, ctypes
from pprint import pprint

#Set variables.
hits = 0
total = 0

#Set Instagram SessionID from cookies
sessionid = ''
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'

#Gets User's Images.
def getimages(username, userid, cursor=''):
    global hits, total
    url = "https://www.instagram.com/graphql/query"
    
    querystring = {"query_hash":"69cba40317214236af40e7efa697781d", "variables":"{\"id\":\""+ userid +"\",\"first\":12,\"after\":\""+cursor+"\"}"}
    
    headers = {
        'cookie': f'sessionid={sessionid};',
        'authority': "www.instagram.com",
        'accept': "*/*",
        'accept-language': "en-US,en;q=0.9",
        'cache-control': "no-cache",
        'pragma': "no-cache",
        'referer': "https://www.instagram.com/",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        'sec-fetch-site': "same-origin",
        'sec-gpc': "1",
        'user-agent': useragent,
        'x-requested-with': "XMLHttpRequest"
        }
    
    r = requests.get(url, headers=headers, params=querystring)
    data = r.json()['data']['user']['edge_owner_to_timeline_media']
    total = data['count']
    
    for i in data['edges']:
        link = i['node']['display_url']
        imgid = i['node']['id']
        downloadimg(link, username)
        hits += 1

    if data['page_info']['has_next_page']:
        end_cursor = data['page_info']['end_cursor']
        getimages(username, userid, end_cursor)
    else:
        print('Finished')
        exit()
   
#Downloads the images.
def downloadimg(link, username):
    ensure_dir(f'images/{username}')
    r = requests.get(link)
    name = link.split('/')[5].split('_')[2]
    try:
        with open(f'images/{username}/{name}.jpg', 'wb') as f:
            f.write(r.content)
            print(f'Downloading PFP - [{username}/{name}.jpg]')
    except Exception as e:
        print(str(e))
        pass

#Generates a random string for filenames.
def randomString(a) -> str:
    letters = string.ascii_letters
    result_str = "".join(random.choice(letters) for i in range(a))
    return result_str

#Creating the folder to sort images.
def ensure_dir(file):
    if not os.path.exists(file):
        os.makedirs(file)

#Getting the user's ID.
def getid(username):
    url = f"https://www.instagram.com/{username}/?__a=1"
    
    headers = {
        'cookie': f'sessionid={sessionid};',
        'authority': "www.instagram.com",
        'accept': "json",
        'accept-language': "en-US,en;q=0.9",
        'cache-control': "no-cache",
        'pragma': "no-cache",
        'sec-fetch-dest': "document",
        'sec-fetch-mode': "navigate",
        'sec-fetch-site': "cross-site",
        'sec-fetch-user': "?1",
        'sec-gpc': "1",
        'upgrade-insecure-requests': "1",
        'user-agent': useragent
        }
    
    r = requests.get(url, headers=headers, allow_redirects=False)
    try:
        userid = r.json()['logging_page_id'].split('_')[1]
        return userid
    except Exception as e:
        if not r.json():
            print(f'No User Found: {username}')
            exit()
        print('Failed for unkown reason.')

#Starts our program.
def start(username):
    userid = getid(username)
    getimages(username, userid)

#Handles the title updates.
def title_worker():
    global hits, total
    while True:
        time.sleep(1)
        ctypes.windll.kernel32.SetConsoleTitleW(f"[INSTAGRAM DOWNLOADER] [{hits} / {total}]")

if __name__ == '__main__':
    #Making sure we have a session ID set.
    if not sessionid:
        print('Please enter your sessionID.')
        exit()

    threading.Thread(target=title_worker).start()
    name = input('Instagram Username:\n')
    start(name)
