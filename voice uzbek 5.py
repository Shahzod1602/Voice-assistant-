import os
import asyncio
import edge_tts
import speech_recognition as sr
import openai
import pygame
import keyboard

API_KEY = ""
openai.api_key = API_KEY

pygame.mixer.init()

# Default settings
selected_language = "uz"
voices = {
    "uz": {"male": "uz-UZ-SardorNeural", "female": "uz-UZ-MadinaNeural"},
    "en": {"male": "en-US-GuyNeural", "female": "en-US-JennyNeural"},
    "ru": {"male": "ru-RU-DmitryNeural", "female": "ru-RU-SvetlanaNeural"},
    "kk": {"male": "kk-KZ-DauletNeural", "female": "kk-KZ-AigulNeural"},
    "ky": {"male": "ky-KG-BakirNeural", "female": "ky-KG-AizatNeural"},
    "tg": {"male": "tg-TJ-JamshedNeural", "female": "tg-TJ-MadinaNeural"}
}
selected_voice_gender = "female"
selected_voice = voices[selected_language][selected_voice_gender]

listening_enabled = True
text_mode = False


def recognize_speech():
    if not listening_enabled:
        return ""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Gapiring / Speak / Говорите / Сөйлеңіз...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=selected_language)
        print(f"Siz / You / Вы / Сіз: {text}")
        return text
    except sr.UnknownValueError:
        print(
            "Ovoz tushunilmadi / Could not understand audio / Не удалось распознать голос / Дауысты тану мүмкін емес.")
        return ""
    except sr.RequestError:
        print("Tarmoq xatosi / Network error / Ошибка сети / Желі қатесі.")
        return ""


def get_ai_response(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": text}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI javob olishda xatolik / Error getting AI response: {e}")
        return "Kechirasiz, hozir javob bera olmayman."


async def speak_edge_tts(text):
    global selected_voice
    output_file = "output.mp3"
    try:
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(output_file)
        if os.path.exists(output_file):
            play_audio(output_file)
        else:
            print("❌ Ovoz fayli yaratilmagan!")
    except Exception as e:
        print(f"TTS ovoz yaratishda xatolik: {e}")


def play_audio(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove(file)
    except Exception as e:
        print(f"Ovoz faylini ijro etishda xatolik: {e}")


def speak_async(text):
    asyncio.run(speak_edge_tts(text))


def change_voice():
    global selected_voice_gender, selected_voice
    selected_voice_gender = "male" if selected_voice_gender == "female" else "female"
    selected_voice = voices[selected_language][selected_voice_gender]
    print(f"Ovoz o'zgartirildi: {selected_voice_gender.capitalize()}")


def change_language():
    global selected_language, selected_voice
    languages = list(voices.keys())
    selected_language = languages[(languages.index(selected_language) + 1) % len(languages)]
    selected_voice = voices[selected_language][selected_voice_gender]
    print(f"Til o'zgartirildi: {selected_language.upper()}")


def toggle_listening():
    global listening_enabled, text_mode
    listening_enabled = not listening_enabled
    text_mode = not text_mode
    if listening_enabled:
        print("Listening mode enabled.")
    else:
        print("Text mode enabled. Enter text and press Enter.")


def read_text():
    text = input("Matnni kiriting: ")
    if text:
        speak_async(text)


def main():
    print("Assalomu alaykum! Ovozli yordamchiga xush kelibsiz!")
    keyboard.add_hotkey("v", change_voice)
    keyboard.add_hotkey("b", change_language)
    keyboard.add_hotkey("t", toggle_listening)
    keyboard.add_hotkey("y", read_text)

    while True:
        if listening_enabled:
            user_input = recognize_speech()
        else:
            user_input = input("Matnni kiriting: ")

        if user_input.lower() in ["chiqish", "exit", "выход", "шығу"]:
            print("Yordamchi o'chirildi.")
            break
        elif user_input:
            ai_response = get_ai_response(user_input)
            print(f"AI: {ai_response}")
            speak_async(ai_response)


if __name__ == "__main__":
    main()