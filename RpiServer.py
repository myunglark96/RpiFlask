from flask import Flask
from flask import request  
import json, time, Rpi.GPIO as GPIO
from collections import OrderedDict

app = Flask(__name__)

#def on_json_loading_failed_return_dict(e):  
#    return [{ "success": fail }]

@app.route('/')
def hello_World():
    return "hello"

@app.route('/led/set', methods=['POST'])
def led_set():
    #request.on_json_loading_failed = on_json_loading_failed_return_dict
    onLight = set()
    offLight = set()
    AllLights = set()
    with open('./LightStatus/onLight.json') as json_file:
        json_data = json.load(json_file)
        print(json_data)

        for status in json_data:
            if json_data[status] and status != "AllLights":
                onLight.add(status)
            elif status == "AllLights":
                for lights in json_data[status]:
                    AllLights.add(lights)
        print(onLight)    
        print(AllLights) 
    for turn_L in request.get_json()["customInfo"]:
        onLight.add(turn_L)
    print(onLight)
    offLight = AllLights-onLight
    print(offLight)

    write_data = OrderedDict()
    write_data["AllLights"]=list(AllLights)
    for turnOn in onLight:
        write_data[turnOn] = True
    for turnOff in offLight:
        write_data[turnOff] = False
    print(json.dumps(write_data, ensure_ascii=False, indent="\t"))
    with open('./LightStatus/onLight.json', 'w', encoding="utf-8") as make_file:
        json.dump(write_data, make_file, ensure_ascii=False, indent="\t")
    return write_data

if __name__ == '__main__':
    app.run()