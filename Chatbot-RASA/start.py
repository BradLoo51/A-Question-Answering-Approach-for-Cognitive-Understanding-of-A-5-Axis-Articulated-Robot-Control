import requests
import pyaudio
import pyttsx3
import speech_recognition as sr
import pvporcupine
import struct
import time

def speak(text):
    '''
    This function takes in any string text and converts it to speech for
    the computer to reply to the user.
    '''
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    print("Alexa: " + text + "\n")
    engine.say(text)
    engine.runAndWait()

def takeCommand():
    '''
    This function recognizes the User's input voice with the microphone and
    translates it to text
    '''
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...", end="", flush=True)
        audio = r.listen(source)
        query = ""

        try:
            print("Recognizing...", end="")
            query = r.recognize_google(audio, language='en-US')
            print(f"User said: {query}")

        except Exception as e:
            print("Exception: " + str(e))

        return query.lower()
    
def rasaQA():
    """
    This function keeps the conversation continuously flowing until 
    it ends or when the user decides to stop it
    """
    bot_message = ""
    while bot_message != "RASA_END":
        userSaid = takeCommand()
        r = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"sender": "User", "message": userSaid})

        for i in r.json():
            bot_message = i['text']
            if bot_message != "RASA_END":
                speak(bot_message)
            else:
                break
    
def main():
    # Initialize the required variables
    porcupine = None
    pa = None
    audio_stream = None

    print("Alexa - Online and Ready!")
    print("Alexa : Awaiting your call ")

    try:
        # Using pyaudio to continuously listen to the audio stream
        porcupine = pvporcupine.create(keywords=["alexa", "computer"])
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate = porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        # Analyze the audio stream and returns 1 when hotwords are detected
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Hotword Detected... ", end="")
                rasaQA()
                time.sleep(1)
                print("Alexa : Awaiting your call ")
    
    finally:
        if porcupine is not None:
            porcupine.delete()

        if audio_stream is not None:
            audio_stream.close()
        
        if pa is not None:
            pa.terminate()


main()


