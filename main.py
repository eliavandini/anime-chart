import json
import time

import requests


gdpr_data = json.load(open("gdpr_data.json"))
try:
    filtered: dict = json.load(open("result.json"))  
except Exception as e:
    print("faled to load result.json:", e)
    filtered = {}
    
for k in filtered:
    filtered[k]["value"].clear()
    filtered[k]["timestamps"].clear()

for i in gdpr_data["activity"]:
    f = [i["object_id"] for i in filtered.values()]
    if i["object_id"] not in f:
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
                romaji
                native
                }
                episodes
                chapters
                type
            }
        }
        '''

        response = requests.post(url, headers=headers, json={'query': query})
        data = response.json()

        # Extracting the relevant information from the response
        print(data, i["object_id"])
        if "errors" in data.keys():
            for n in range(int(dict(response.headers)["Retry-After"])+2, 0, -1):
                print(f"wait for {n:02}", end='\r')
                time.sleep(1)
            print("")
            response = requests.post(url, headers=headers, json={'query': query})
            data = response.json()
            print(data)
        media_info = data["data"]["Media"]

        title_info = media_info.get('title', {})
        english_title = title_info.get('english')
        romaji_title = title_info.get('romaji')
        native_title = title_info.get('native')
        episodes = media_info.get('episodes')
        chapters = media_info.get('chapters')
        type = media_info.get('type')
        # if type == "MANGA":
        #     continue
        
        if english_title is None:
            english_title = romaji_title
        if english_title is None:
            english_title = native_title
        
        if episodes is None:
            episodes = chapters
        
        # if episodes is None:
        #     continue
        
        
        filtered[str(i["object_id"])] = {
            "object_id": i["object_id"],
            "title": english_title,
            "value": [],
            "timestamps": [],
            "episodes": episodes,
            "type": type
        }
    
for k in filtered:
    filtered[k].setdefault("type", "ANIME")
    

for i in gdpr_data["activity"]:
    id = str(i["object_id"])
    if i["action_type"] == 3:
        ep = int(i["object_value"].split(" - ")[-1])
        if filtered[id]["episodes"] is not None:
            if ep <= filtered[id]["episodes"]:
                filtered[id]["value"].append(ep)
        # if filtered[i["object_id"]]["value"][-1] == filtered[i["object_id"]]["episodes"]:
            
        filtered[id]["timestamps"].append(i["updated_at"])
    if i["action_type"] == 1:
        filtered[id]["value"].append(filtered[id]["episodes"])
        filtered[id]["timestamps"].append(i["updated_at"])
        filtered[id]["value"].append(None)

for k in filtered:
    filtered[k].setdefault("type", "ANIME")
    if len(filtered[k]["value"]) > 0:
        if filtered[k]["value"][-1] is None:
            filtered[k]["value"].pop(-1)
    if len(filtered[k]["timestamps"]) > 0:
        filtered[k]["value"] = [0] + filtered[k]["value"]
        filtered[k]["timestamps"] = [filtered[k]["timestamps"][0]] + filtered[k]["timestamps"]
        temp_time = []
        temp_value = []
        Nones = 0
        for ind in range(len(filtered[k]["value"])):
            temp_time.append(filtered[k]["timestamps"][ind-Nones])
            temp_value.append(filtered[k]["value"][ind])
            if filtered[k]["value"][ind] is None:
                temp_time.append(filtered[k]["timestamps"][ind-Nones])
                Nones+=1
                temp_value.append(0)
        filtered[k]["timestamps"] = temp_time
        filtered[k]["value"] = temp_value
    # if k == "30":
    #     print("huiii")
        
l = {key:{k:v for (k,v) in value.items() if k not in ["value", "timestamps"]} for (key, value) in filtered.items()}
json.dump({key:{k:v for (k,v) in value.items() if k not in ["value", "timestamps"]} for (key, value) in filtered.items()}, open("result.json", "w"))        

# for key, val in filtered:
#     if len(val["value"]) == 0 or len(val["timestamp"]) == 0:
#         filtered.pop(key)
#     else:
#         val["value"] = [0] + val["value"]
#         val["timestamp"] = [val["timestamp"][0]] + val["timestamp"]

# print(filtered)
# json.dump(filtered, open("result.json", "w"))

import json
import plotly.express as px
from datetime import datetime

# data = filtered
# Convert timestamps to datetime objects
filtered_list = list(sorted(list(filtered.items()), key=lambda k: k[1]["title"]))

for key, entry in filtered_list:
    entry["timestamps"] = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in entry["timestamps"]]

# Prepare data for plotting
plot_data = []
for key, entry in filtered_list:
    for timestamp, value in zip(entry["timestamps"], entry["value"]):
        plot_data.append({"Title": entry["title"], "Timestamp": timestamp, "Value": value})

# Create Plotly figure
fig = px.line(plot_data, x="Timestamp", y="Value", color="Title", markers=True, line_group="Title",
              title="Time-line Graph", labels={"Value": "Y-Axis Label", "Timestamp": "X-Axis Label"},
              template="plotly_white")

# Show the figure
fig.show()