import openai
import pyttsx3
import speech_recognition as sr

openai.api_key = ""
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 0.9)


def speak(text):
    engine.setProperty("voice", "english")
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            return query
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Speech recognition service is unavailable."
        except sr.WaitTimeoutError:
            return "You didn't say anything."


def ask_openai(prompt):
    # Predefined response for self-introduction
    introduction_response = """
I am Shawn Robot, an artificial intelligence assistant. My primary task is to simplify communication between humans and technology and increase efficiency. Here are the tasks I can perform:

1. **Data Search and Analysis:** I help you quickly find and analyze the information you need — from the latest news on the internet to complex technical analyses.

2. **Creative Assistance:** I can assist in creating articles, presentation scripts, slogans, or content ideas.

3. **Task Management:** I help plan your daily tasks, add reminders, organize meetings, and set priorities.

4. **Code Writing and Editing:** I can write code in various programming languages, detect errors, and help troubleshoot issues.

5. **Technical Consultation:** I offer advice on mechanical or electronic projects and recommend technical solutions.

6. **AI Integration:** I can assist in incorporating AI algorithms into your projects and optimizing them.
"""
    # Keywords to trigger the predefined response
    if any(keyword in prompt.lower() for keyword in ["tell me about yourself", "who are you", "what do you do", "introduce yourself"]):
        return introduction_response.strip()

    # Default OpenAI response for other queries
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Shawn, a helpful English-speaking assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"


def main():
    speak("Hello! I am Shawn. How can I assist you today?")
    while True:
        user_input = listen()
        if user_input.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye!")
            break
        print(f"You said: {user_input}")
        response = ask_openai(user_input)
        print(f"Shawn: {response}")
        speak(response)


if __name__ == "__main__":
    main()
