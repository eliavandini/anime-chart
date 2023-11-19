import json
import time

import requests


data = json.load(open("gdpr_data.json"))
filtered = {}
for i in data["activity"]:
    
    if i["object_id"] not in list(filtered.keys()) or i["action_type"] == 1:
        url = 'https://graphql.anilist.co'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        query = '''
            {
            Media(id: ''' + str(i["object_id"]) + ''') {
                title {
                english 
                }
                episodes
            }
        }
        '''

        response = requests.post(url, headers=headers, json={'query': query})
        data = response.json()

        # Extracting the relevant information from the response
        print(data)
        if "errors" in data.keys():
            time.sleep(int(dict(response.headers)["Retry-After"])+2)
            response = requests.post(url, headers=headers, json={'query': query})
            data = response.json()
            print(data)
        media_info = data["data"]["Media"]

        title_info = media_info.get('title', {})
        english_title = title_info.get('english')
        episodes = media_info.get('episodes')

    if i["object_id"] not in list(filtered.keys()):
        filtered[i["object_id"]] = {
            "object_id": i["object_id"],
            "title": english_title,
            "value": [],
            "timestamps": []
        }
    if i["action_type"] == 3:
        filtered[i["object_id"]]["value"].append(int(i["object_value"].split(" - ")[-1]))
        filtered[i["object_id"]]["timestamps"].append(i["updated_at"])
    if i["action_type"] == 1:
        filtered[i["object_id"]]["value"].append(episodes)
        filtered[i["object_id"]]["timestamps"].append(i["updated_at"])
print(filtered)
json.dump(filtered, open("result.json", "w"))

