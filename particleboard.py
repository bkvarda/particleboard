import json, StringIO, requests, time, ConfigParser
from sseclient import SSEClient
from datetime import datetime

#get configuration stuff
Config = ConfigParser.ConfigParser()
Config.read('particleboard.conf')
api_key = Config.get('Particle','ApiKey')
print_events = Config.get('Options','PrintEvents')
batch_size = int(Config.get('Options','BatchSize'))
batch_pause = int(Config.get('Options','BatchPause'))
flume_http_source = Config.get('Options','FlumeHttpSource')

uri = 'https://api.particle.io/v1/events?access_token=' + api_key
count = 0

#not sure if these headers are necessary even, but leaving
headers = {"Accept-Content":"application/json; charset=UTF-8"}
messages = SSEClient(uri)
for msg in messages:
    event = '"'+msg.event+'"'
    data = msg.data
    payload = {}
    if(data):
        json_out = '{"event":' + event + "," + '"data":' + data + '}'
        
        #try loop because some data is wonky and causes exceptions.
        try:
            obj = json.loads(json_out)
            event = '"' + obj["event"] + '"'
            data  = obj["data"]["data"].replace(",","")
            published_at = obj["data"]["published_at"]
            ttl = obj["data"]["ttl"]
            coreid = '"' + obj["data"]["coreid"] + '"'
            parsed_time = time.strptime(published_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", parsed_time)
            payload["body"] = formatted_time + "," + event + "," + data + "," + coreid + "," + ttl
        except:
            pass
        
        #need to turn individual events into an array because Flume http source requires it
        final_obj = '[' + json.dumps(payload) + ']'

        #if event printing is enabled, send to console
        if(print_events == 'enabled'):
            print(str(final_obj))
        
        #r = requests.post("http://quickstart.cloudera:5140", headers=headers,  data = final_obj) 
        count += 1
        
        #once configured batch is met, wait for configured time
        if count >= batch_size:
            print('Wating for ' + str(batch_pause) + ' seconds')
            time.sleep(batch_pause)
            count = 0
