#!/usr/bin/python3

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) #Supress scapy warnings
from scapy.all import *
import argparse
import json
import hashlib
from http.client import HTTPSConnection
import urllib
from tornado import websocket, web, httpserver, ioloop

class WebSocketSever(websocket.WebSocketHandler):

  def check_origin(self, origin):
    return True

  def open(self):
    print("[+] Client connected")
    try:
      sniffer(self)
    except PermissionError as e:
      print("[!] Got permission error. Run as root!")
      ioloop.IOLoop.instance().stop()
    
  def on_message(self, message):
    print("[+] Got message: " + str(message))

  def on_close(self):
    print("[-] Connection closed") 

class FrameHandler:
  callback = None
  seen = None
  config = None
  outFile = None
  def __init__(self, cb, cfg, out):
    self.callback = cb
    self.seen = []
    self.config = cfg
    self.outFile = out

  def handler(self, frame):
    if(frame.haslayer(Dot11) and (frame.type == 0x0 or frame.type==0x04)):
      try:
        probeSSID = str(frame.info)[2:-1]
        if(len(probeSSID) > 0):
          info = {}
          info['device'] = frame.addr2
          info['ssid'] = probeSSID
          if(self.checkDuplicate(info) == False):
            self.addSeen(info)
            locations = self.getLocation(probeSSID)
            info['location'] = locations
            print("[+] To client: " + json.dumps(info))
            self.callback.write_message(json.dumps(info))
            if(self.outFile is not None):
              with open(self.outFile, 'a') as file:
                file.write(json.dumps(info) + "\n")
      except Exception as e:
        pass #Ignore exceptions
  
  def getLocation(self, ssid):
    locations = []
    try:      
      conn = HTTPSConnection("api.wigle.net")
      headers = { 'Authorization' : 'Basic %s' % self.config["wigleAuthToken"] }
      conn.request('GET', '/api/v2/network/search?onlymine=false&freenet=false&paynet=false&ssid=' + urllib.parse.quote_plus(ssid), headers=headers)
      resp = conn.getresponse()
      data = str(resp.read())[2:-1]
      data = data.replace("true", "\"True\"").replace("false", "\"False\"")
      dataJson = json.loads(data)
      if(dataJson['success'] == "False" and dataJson['error'] == "too many queries today"):
        print("[!] WIGLE API QUERY LIMIT REACHED. Sending  coordinates 0.0 0.0")
        locations.append({})
        locations[len(locations)-1]['lat'] = 0.0
        locations[len(locations)-1]['lng'] = 0.0
        locations.append({})
        locations[len(locations)-1]['lat'] = 0.0
        locations[len(locations)-1]['lng'] = 0.0
      elif(dataJson['results'] and len(dataJson['results']) > 0):
        for r in range(len(dataJson['results'])):
          locations.append({})
          locations[len(locations)-1]['lat'] = dataJson['results'][r]['trilat']
          locations[len(locations)-1]['lng'] = dataJson['results'][r]['trilong']
        return locations
    except Exception as e:
      print("[!] Error getting lat and long for " + ssid)
      print(e)
      print("Response: " + data)
      
      
    return locations 
    
  def addSeen(self, info): 
    try:
      self.seen.append(hashlib.md5(str(info).encode('utf-8')).hexdigest())
    except:
      print("[!] Error. Could not add SSID to seen probes")
      
  def checkDuplicate(self, info):
    try:
      return (hashlib.md5(str(info).encode('utf-8')).hexdigest() in self.seen)
    except:
      print("[!] Error. Could not check if SSID has been seen")
      return True
  
def sniffer(context):
  frameHandler = FrameHandler(context, getConfig(), params.write)
  print("[+] Listening for probe requests on interface " + params.interface + "...")
  if(params.write is not None):
    print("[+] Copying output to " + params.write)
  print("[+] Use ctrl+c to stop")
  sniff(iface=params.interface, prn=frameHandler.handler, store=0)
  ioloop.IOLoop.instance().stop()
  print("[+] Stopped.")
  
def getConfig():
  file = open("config.js", 'r')
  configData = file.read().split("var config = ")[1]
  config = json.loads(configData)
  return config
  
def main():
  global params  
  parser = argparse.ArgumentParser(description="DESCRIPTION")
  parser.add_argument('-i', '--interface', help="interface to capture on")
  parser.add_argument('-w', '--write', help="Write data to file")

  params = parser.parse_args()
  if(not params.interface):
    print("[!] Please provide an interface to listen on using the -i option")
    return

  print("[+] Getting config from config.js")
  config = getConfig()

  print("[+] Setting up web socket server...")
  app = web.Application([(r'/', WebSocketSever),])

  http_server = httpserver.HTTPServer(app)
  http_server.listen(config["serverPort"])
  print("[+] Web socket ready")
  
  ioloop.IOLoop.instance().start()
    
if __name__ == '__main__':
  main()
