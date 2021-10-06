#!/usr/bin/env python3

from cloudant import CouchDB
from dotenv import load_dotenv
from flask import Flask
from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time
import requests
from requests.exceptions import HTTPError
import jsonify
import shortuuid

# Load secrets
load_dotenv()

token = os.getenv('TOKEN')
org_id = os.getenv('ORG_ID')
neutron_url = os.getenv('NEUTRON')
cdb_url = os.getenv('CDB_URL')
cdb_user = os.getenv('CDB_USER')
cdb_pass = os.getenv('CDB_PASS')
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

# Setup DB connection strings

client = InfluxDBClient(url=neutron_url, token=token)
cdb = CouchDB(cdb_user, cdb_pass, url=cdb_url, connect=True, auto_renew=True)
cdb_accounts = cdb['neutron_accounts']
cdb_neutrinos = cdb['neutrinos']

write_api = client.write_api(write_options=SYNCHRONOUS)

### Helper Functions
def generateNeutrinoUUID():
    neutrino_uuid = shortuuid.uuid()
    return neutrino_uuid

def generateNeutrinoToken(neutrino_uuid):
    tokenURL = neutron_url + "/api/v2/authorizations"
    description = "neutrino-" + neutrino_uuid
    payload = {"status": "active", "description": "", "orgID": "", "permissions": [{"action": "write", "resource": { "type": "buckets", "name": "default"}}]}
    payload['description'] = description
    payload['orgID'] = org_id
    response = requests.post(tokenURL, json=payload, headers={'Authorization': 'Token {}'.format(token), 'Content-type': 'application/json'})
    resp = response.json()
    if response.status_code == 201:
        new_token = resp['token']
        new_status = resp['status']
        final_response = {"status": new_status, "token": new_token}
        return final_response
    else:
        resp = response.json()
        error_msg = resp['message']
        return error_msg

### API
app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route('/account/<account_id>', methods = ['GET', 'POST', 'DELETE'])
@auth.login_required
def account(account_id):
    if request.method == 'GET':
        account = account_id in cdb_accounts
        if account:
            return "Account {} exists".format(account_id)
        else:
            return "Account {} does not exist".format(account_id)
    
    if request.method == 'POST':
        data = request.json
        account = account_id in cdb_accounts
        if account:
            doc = cdb_accounts[account_id]
            if data['name']:
                doc['name'] = data['name']
            if data['address']:
                doc['address'] = data['address']
            if data['neutrinos']:
                doc['neutrinos'] = data['neutrinos']
            doc.save()
            return "Account {} updated".format(account_id)
        else:
            newAccount = {"_id": account_id, "name": data['name'], "address": data['address'], "neutrinos": data['neutrinos']}
            cdb_accounts.create_document(newAccount)
            return "Account {} created".format(account_id)

    if request.method == 'DELETE':
        account = account_id in cdb_accounts
        if account:
            doc = cdb_accounts[account_id]
            doc.delete()
            return "Account {} deleted".format(account_id)
        else:
            return "Account {} does not exist".format(account_id)

@app.route('/neutrinos/<neutrino_id>', methods = ['GET', 'DELETE'])
@auth.login_required
def neutrinos(neutrino_id):
    if request.method == 'GET':
        neutrino = neutrino_id in cdb_neutrinos
        if neutrino:
            doc = cdb_neutrinos[neutrino_id]
            results = {"_id": doc['_id'], "_rev": doc['_rev'], "location_name": doc['location_name'], "customer": doc['customer']}
            return results
        else:
            return "Neutrino {} does not exist.".format(neutrino_id)

@app.route('/neutrinos/new', methods = ['POST'])
@auth.login_required
def neutrinosNew():
    if request.method == 'POST':
        neutrino_uuid = generateNeutrinoUUID()
        neutrino_token_response = generateNeutrinoToken(neutrino_uuid)

        if neutrino_token_response['status']:
            neutrino_token = neutrino_token_response['token']
            newNeutrino = {"_id": "", "location_name": "default", "customer": "default", "token": ""}
            newNeutrino['_id'] = neutrino_uuid
            newNeutrino['token'] = neutrino_token 
            cdb_neutrinos.create_document(newNeutrino)
            return neutrino_token_response['token']
        else:
            return neutrino_token_response


@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == api_key and password == api_secret:
            return True
        else:
            return False
    return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)