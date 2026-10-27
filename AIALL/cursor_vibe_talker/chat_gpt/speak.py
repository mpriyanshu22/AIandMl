import pyttsx3

engine = pyttsx3.init()

def speak(text):
    print(f'AI: {text}')
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    speak('Namaste Priyanshu bhai, main ab bol raha hoon. Kaise ho aap?')
