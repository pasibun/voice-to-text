from os import path
from pydub import AudioSegment
import subprocess
import argparse
import io
import glob
import os

file = 'audio.mp3'
dest = 'audio.wav'
taal_code = "nl-NL"

ouputFile = "/home/pi/git/voice/audio.txt"

def transcribe_file(speech_file):
    """Transcribe the given audio file asynchronously."""
    from google.cloud import speech

    client = speech.SpeechClient()

    # [START speech_python_migration_async_request]
    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=taal_code,
    )

    # [START speech_python_migration_async_response]
    operation = client.long_running_recognize(
        request={"config": config, "audio": audio}
    )
    # [END speech_python_migration_async_request]

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    f = open(ouputFile, "a+")
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))
        f.write(result.alternatives[0].transcript)
    f.close()
    
def converting_to_1_min_files():    
    print("Converting wav file to smaller 1 min files.")
    command = 'sox {} /home/pi/git/voice/parts/output.wav trim 0 59 : newfile : restart'.format(dest)
    subprocess.call(command, shell=True)
    
def convert_output_to_raw(): 
    print("Converting file to raw.")
    count = 1
    input = sorted(glob.glob("/home/pi/git/voice/parts/*.wav"))
    for x in input:
        output = "/home/pi/git/voice/output/output-{}.raw".format(count)
        command = 'sox {} --rate 16000 --bits 16 --encoding signed-integer --endian little --channels 1 {}'.format(x,output)    
        print(command)
        count+=1
        flag_done = subprocess.call(command, shell=True)
    
def mp3_to_wav():
    print("Converting mp3 to wav")
    sound = AudioSegment.from_mp3(file)
    sound.export(dest, format="wav")
    print("Converting ready..")

def cleaning():
    print("Cleaning project.")
    open(ouputFile, 'w').close()        
    files = glob.glob('/home/pi/git/voice/parts/*')
    files2 = glob.glob('/home/pi/git/voice/output/*')
    files3 = glob.glob('/home/pi/git/voice/*.wav')
    for f in files:
        os.remove(f)
    for f in files2:
        os.remove(f)
    for f in files3:
        os.remove(f)

if __name__ == "__main__":    
    cleaning()
    mp3_to_wav()    
    converting_to_1_min_files()    
    convert_output_to_raw()    
    output = sorted(glob.glob("/home/pi/git/voice/output/*.raw"))
    print("voice to text:")
    for x in output:
        transcribe_file(x)