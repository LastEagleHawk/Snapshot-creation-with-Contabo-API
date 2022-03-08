#!/usr/bin/env python3

##########################################################
####### Create snapshots for Contabo VPS using API     ###
##########################################################

import requests
from requests.structures import CaseInsensitiveDict
from urllib.parse import urlencode
from urllib.error import HTTPError
from datetime import date
import json
import logging

# Define API credentials
CLIENT_ID="Insert Client ID"
CLIENT_SECRET="Insert Client Secret"
API_USER="Insert API Username"
API_PASSWORD="Insert API Password"
LOGFILE="Chose a file path for log"

# Creating and Configuring Logger
Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = LOGFILE,
                    filemode = "w",
                    format = Log_Format, 
                    level = logging.DEBUG)
logger = logging.getLogger()
logger.info("Inizio esecuzione script")

class Contabo:
    def __init__(self, client_id, client_secret, api_user, api_password):
        # Initialize object with credentials
        self.client_id=client_id
        self.client_secret=client_secret
        self.api_user=api_user
        self.api_password=api_password

    def GetToken(self):
        # Pass credentials and execute request to get token  
        url = "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token"
        headers = { 'Content-type': 'application/x-www-form-urlencoded' }
        data = urlencode({'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'password', 'username': self.api_user, 'password': self.api_password})
        response = requests.post(url, headers=headers, data=data)
        if(response.status_code==200):
            self.token = response.json().get('access_token')
            logger.info("Token ricevuto!")
        else:
            logger.error("Errore nella richiesta per ottenere il token")
            
    
    def GetInstancesInfo(self):
        # Get instances information
        url = "https://api.contabo.com/v1/compute/instances"
        headers = { 'Authorization' : 'Bearer ' + self.token, 'x-request-id': '51A87ECD-754E-4104-9C54-D01AD0F83406' }
        response = requests.get(url, headers=headers)
        instances = response.json().get('data')
        if(response.status_code==200):
            self.instances = instances
            logger.info("Informazioni sulle istanze ricevute!")
        else:
            logger.error("Errore nella richiesta per ottenere informazioni delle istanze")

    def GetSnapshotsAvailable(self, instanceId):
        # Get Snapshots Available
        url = "https://api.contabo.com/v1/compute/instances/"+str(instanceId)+"/snapshots"
        headers = { 'Content-Type' : 'application/json', 'Authorization' : 'Bearer ' + self.token, 'x-request-id' : 'c185303b-346c-4feb-bdd5-f524f14ecd09' }
        response = requests.get(url, headers=headers)
        self.name_instance = instance['name']
        self.number_snapshots = len(response.json().get('data'))
        self.snapshots = response.json().get('data')
        if(response.status_code==200):
            self.instances = instances
            logger.info("Informazioni sugli snapshots ricevuti!")
        else:
            logger.error("Errore nella richiesta per ottenere informazioni delle istanze")
    
    def DeleteSnapshot(self, instanceId, snapshotId):
        # Delete Snapshot
        url = str("https://api.contabo.com/v1/compute/instances/"+str(instanceId)+"/snapshots/"+str(snapshotId))
        headers = { 'Accept' : 'application/json', 'Authorization' : 'Bearer ' + self.token, 'x-request-id' : '3d0a51c3-3117-4e57-af68-d1b8b443e48d' }
        response = requests.delete(url, headers=headers)
        if(response.status_code==204):
            self.instances = instances
            logger.info("Snapshot "+str(snapshotId)+" dell'istanza "+str(instanceId)+" eliminato!")
        else:
            logger.error("Errore nella eliminazione dello snapshot "+str(snapshotId))
    
    def CreateNewSnapshot(self, instanceId, name):
        # Create a new Snapshot Instance
        datenow = date.today().strftime("%b-%d-%Y")
        url = 'https://api.contabo.com/v1/compute/instances/'+str(instanceId)+'/snapshots'
        headers = { 'Content-type': 'application/x-www-form-urlencoded', 'Authorization' : 'Bearer ' + self.token, 'x-request-id' : 'cafa9c23-8bb9-43cb-aaf2-9b8a2ac81eef' }
        data = { 'name': str(name) + '-' + str(datenow), 'description': 'Snapshot created from script at ' + str(datenow) }
        response = requests.post(url, headers=headers, data=data)
        if(response.status_code==201):
            self.instances = instances
            logger.info("Nuovo snapshot dell'istanza "+str(instanceId)+" creato con successo!!")
        else:
            logger.error("Errore nella creazione dello snapshot dell'istanza "+str(instanceId))

    def GetSnapshots(self):
        return self.snapshots

    def GetInstances(self):
        return self.instances

    def GetNumberSnapshots(self):
        return self.number_snapshots
    
    def GetNameInstance(self):
        return self.name_instance

try:
    # Initialize Object
    VPS = Contabo(CLIENT_ID,CLIENT_SECRET,API_USER,API_PASSWORD)
    VPS.GetToken()
    VPS.GetInstancesInfo()
    instances = VPS.GetInstances()

    # For every instance VPS delete old snapshots and create new snapshots
    for instance in instances:
        VPS.GetSnapshotsAvailable(instance['instanceId'])
        
        number_snapshots=VPS.GetNumberSnapshots()
        # If there is one or more snapshot
        if(number_snapshots>=1):
            snapshots = VPS.GetSnapshots()
            # Delete old Snapshot for that instance
            for snapshot in snapshots:
                VPS.DeleteSnapshot(instance['instanceId'],snapshot['snapshotId'])

            #Create a new Snapshot Instance
            VPS.CreateNewSnapshot(instance['instanceId'],instance['name'])
        else:
            # Create a new Snapshot Instance
            VPS.CreateNewSnapshot(instance['instanceId'],instance['name'])
except Exception as ex:
    logger.error("Si è verificata una eccezione!!")