from wit import Wit
import azure.cognitiveservices.speech as speechsdk
import paramiko
from paramiko import SSHClient, AutoAddPolicy
import operator
import subprocess
import os
# from google.cloud import texttospeech
import requests
import tts
from tts import main
import time

def get_weather_info(city):
    
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+'&appid=e177b49016dbc7187623087a71c7597e')
    json_object = r.json()

    condition = str(json_object['weather'][0]['description'])
    temp_k = float(json_object['main']['temp'])
    temp_f = int((temp_k - 273.15) * 1.8 + 32)

    # Conditions
    return temp_f, condition

def get_weather_audio(city):

    temp_f, condition = get_weather_info(city)
    speech = "The weather is" + str(temp_f) + "fahrenheit and the condition is" + str(condition)

    main(speech)

# Setting up Wit.ai intents classification
access_token = 'ISTGG3Z5DJKT7O7MRSDLMIQPOG7CAYU7'
wit = Wit(access_token)

# Setting up Azure speech-text services
speech_key, service_region = "e61387a2619540e58a885247bff810ee", "westus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key , region=service_region)

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# Setting up SSH to Pi
username='pi'
password='dragonhacks'
host = '144.118.58.188'
# host = '169.254.226.136'

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect(host, username=username, password=password, port=22)



# Starts speech recognition, and returns after a single utterance is recognized. The end of a
# single utterance is determined by listening for silence at the end or until a maximum of 15
# seconds of audio is processed.  The task returns the recognition text as result. 
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query. 
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.

# while True:

print("Say something...")
result = speech_recognizer.recognize_once()

# Checks result.
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
    
resp = wit.message(result.text)
print(result.text)
print('Wit.ai response: ' + str(resp))

max_intent = 0.0
res = 'NA'

intent_dict = resp['entities']
for intent, list_ in intent_dict.items() :

    if float(list_[0]['confidence']) > max_intent:
        max_intent = float(list_[0]['confidence'])
        res = list_[0]['value']

location = None
if res == 'get_weather':
    location = resp['entities']['location'][0]['value']
    print(resp['entities']['location'][0]['value'])

# Command SSH on Pi
print('Intent',res)

if res == 'get_weather':

    if location is not None:
        get_weather_audio(location)

    # stdin, stdout, stderr = ssh.exec_command('sudo rm /home/pi/Desktop/Code/audio-data.mp3')
    os.system('scp audio-data.wav pi@' + host + ':Desktop/Code/')
    # time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('vlc /home/pi/Desktop/Code/audio-data.wav')
    # stdin, stdout, stderr = ssh.exec_command('mpg123 /home/pi/Desktop/Code/audio-data.mp3')
    print(stderr.read())

elif res == 'intro_song':
    stdin, stdout, stderr = ssh.exec_command('vlc /home/pi/Desktop/Code/Intro_Song.mp3')

elif res == 'strip_on':
    stdin, stdout, stderr = ssh.exec_command('sudo python /home/pi/Desktop/Code/strip_on.py')

elif res == 'strip_off':
    stdin, stdout, stderr = ssh.exec_command('sudo python /home/pi/Desktop/Code/strip_off.py')

elif res == 'light_on':
    stdin, stdout, stderr = ssh.exec_command('sudo python /home/pi/Desktop/Code/light_on.py')

elif res == 'light_off':
    stdin, stdout, stderr = ssh.exec_command('sudo python /home/pi/Desktop/Code/light_off.py')

    # print('Please wait ...')
    # print('...')
    # time.sleep(2)