from flask import Flask
from flask import request, redirect, url_for
import requests
import json, time 
import RPi.GPIO as GPIO
from collections import OrderedDict

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)

Ip = {
        "livingroom" : 'http://127.0.0.1:5000',
        "bedroom" : 'http://127.0.0.1:5000',
        "kitchen" : 'http://127.0.0.1:5000'
        }

@app.route('/')
def hello_World():
    return "hello"

@app.route('/test')
def test():
    led=4
    GPIO.setup(led, GPIO.OUT)
    time.sleep(1)
    return 'test'

@app.route('/lightOn')
def lightOn():
    GPIO.setup(4, GPIO.OUT)
    time.sleep(1)   
    GPIO.output(4, False)
    time.sleep(1)
    return "lightOn"

@app.route('/lightOff')
def lightOff():
    GPIO.setup(4, GPIO.OUT)
    time.sleep(1)
    GPIO.output(4, True)
    time.sleep(1)
    return "lightOff"

@app.route('/led/status')
def returnStatus():
    with open('./LightStatus/onLight.json') as json_file:
        json_data = json.load(json_file)
        print(json_data)
    return json.dumps(json_data, indent=4, default=str)

@app.route('/led/set', methods=['POST'])
def led_set():
    #request.on_json_loading_failed = on_json_loading_failed_return_dict
    onLight = set()
    offLight = set()
    AllLights = set()
    with open('./LightStatus/onLight.json') as json_file:
        json_data = json.load(json_file)

        for status in json_data:
            if json_data[status] and status != "AllLights":
                onLight.add(status)
            elif not json_data[status] and status != "AllLights":
                offLight.add(status)
            elif status == "AllLights":
                for lights in json_data[status]:
                    AllLights.add(lights)

    if(request.get_json().get("customInfo") is not None):
        for turn_L in request.get_json()["customInfo"]:
            onLight.add(turn_L)
        offLight = AllLights-onLight

    elif(request.get_json().get("lightOn") is not None):
        for turn_L in request.get_json()["lightOn"]:
            onLight.add(turn_L)
        offLight = AllLights-onLight

    elif(request.get_json().get("lightOff") is not None):
        for turnoff_L in request.get_json()["lightOff"]:
            offLight.add(turnoff_L)
        onLight = AllLights-offLight

    else: 
        return "error"

    for OL in onLight:
        resOn = requests.get(Ip[OL]+'/lightOn')

    for OfL in offLight:
        resOff = requests.get(Ip[OfL]+'/lightOff')
        
    write_data=OrderedDict()
    write_data["AllLights"]=list(AllLights)
    for turnOn in onLight:
        write_data[turnOn] = True
    for turnOff in offLight:
        write_data[turnOff] = False
    print(write_data)
    print(json.dumps(write_data, indent=4, default=str))
    with open('./LightStatus/onLight.json', 'w') as make_file:
        make_file.write(json.dumps(write_data, indent=4, default=str))
    return "success"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
