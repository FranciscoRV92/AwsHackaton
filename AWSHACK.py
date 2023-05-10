import boto3
import time

from playsound import playsound
import os
from contextlib import closing
import sys
import subprocess
from tempfile import gettempdir
import pyttsx3
import pygame
import pyaudio




id1 = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0'
engine = pyttsx3.init()
engine.setProperty('voice',id1)

session = boto3.Session(
aws_access_key_id='YOUR_ACCES_KEY',
aws_secret_access_key='YOUR_SECRET_ACCES_KEY'
)

rekognition = session.client('rekognition','eu-central-1')
s3 = session.client('s3','eu-central-1')
polly = session.client('polly','eu-central-1')
translator = session.client('translate','eu-central-1')
bucketname ='awshackaton'
videoname = 'video2.mp4'

p = pyaudio.PyAudio()

auxiliar = ""

# Start video label recognition job
startLabelDetection = rekognition.start_label_detection(
    Video={
        'S3Object': {
            'Bucket': bucketname,
            'Name': videoname,
        }
    },
)

labelsJobId = startLabelDetection['JobId']
print("Job Id: {0}".format(labelsJobId))

# In production use cases, you would usually use StepFunction or SNS topic to get notified when job is complete.
getObjectDetection = rekognition.get_label_detection(
    JobId=labelsJobId,
    SortBy='TIMESTAMP'
)

while(getObjectDetection['JobStatus'] == 'IN_PROGRESS'):
    
    print('.', end='')
 
    getObjectDetection = rekognition.get_label_detection(
    JobId=labelsJobId,
    SortBy='TIMESTAMP')
    
for obj in getObjectDetection['Labels']:
    ts = obj ["Timestamp"]
    cconfidence = obj['Label']["Confidence"]
    oname = obj['Label']["Name"]
    #print(obj)
    traducido = translator.translate_text(Text=oname, SourceLanguageCode="en", TargetLanguageCode="es")
    response = polly.synthesize_speech(Text=auxiliar, OutputFormat="mp3", VoiceId="Carmen",LanguageCode="es-ES")  
    #print("Audio NO GUARDADO")
    if cconfidence > 85:
        volume = engine.getProperty('volume')
        auxiliar += traducido['TranslatedText'] + "\n"
        #engine.setProperty('volume', volume+1)
        #engine.say(traducido['TranslatedText'])
        #Pronunciar mensaje:
        #engine.runAndWait()
    
    #print("Found flagged object at {} ms: {} (Confidence: {})".format(ts, oname, round(cconfidence,2)))
        

print(auxiliar)   
engine.save_to_file(auxiliar, "C:/Users/0018280/Desktop/audio.mp3")
engine.runAndWait()
theObjects = {}

# Display timestamps and objects detected at that time
strDetail = "Objects detected in video<br>=======================================<br>"
strOverall = "Objects in the overall video:<br>=======================================<br>"

# Objects detected in each frame
