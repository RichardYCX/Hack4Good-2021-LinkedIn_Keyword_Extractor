import config
import json
import requests

file_name = 'RY.json'

with open(file_name, 'r') as json_file:
    person_dict = json.load(json_file)

# print(json.dumps(person_dict, indent=4, sort_keys=True))
text = ""
for x in person_dict["Interests"].keys():
    if x == 'Companies':
        pass
    elif x == 'Influencers':
        y = person_dict["Interests"][x]
        for z in y:
            text += z["Description"] + ' '

if "Recent Activities" in person_dict:
    for x in person_dict["Recent Activities"]:
            y = x["Author Description"]
            text += (y+' ') if y is not None else ''

if text != "":
    r = requests.post(
        "https://api.deepai.org/api/text-tagging",
        data={'text': text},
        headers={'api-key': config.api_key}
    )

    print(r.json()['output'])
else:
    print("no keywords")