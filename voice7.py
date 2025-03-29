import os
import asyncio
import edge_tts
import speech_recognition as sr
import openai
import pygame
import keyboard
from PyQt5 import QtWidgets, QtGui

API_KEY =""
openai.api_key = API_KEY

pygame.mixer.init()

voices = {
    "uz": {"male": "uz-UZ-SardorNeural", "female": "uz-UZ-MadinaNeural"},
    "en": {"male": "en-US-GuyNeural", "female": "en-US-JennyNeural"},
    "ru": {"male": "ru-RU-DmitryNeural", "female": "ru-RU-SvetlanaNeural"},
    "kk": {"male": "kk-KZ-DauletNeural", "female": "kk-KZ-AigulNeural"},
    "ky": {"male": "ky-KG-BakirNeural", "female": "ky-KG-AizatNeural"},
    "tg": {"male": "tg-TJ-JamshedNeural", "female": "tg-TJ-MadinaNeural"}
}


class VoiceAssistantApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.selected_language = "uz"
        self.selected_voice_gender = "female"
        self.selected_voice = voices[self.selected_language][self.selected_voice_gender]
        self.mode = "speaking"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.language_label = QtWidgets.QLabel("Select Language:")
        self.layout.addWidget(self.language_label)
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(voices.keys())
        self.language_combo.currentTextChanged.connect(self.change_language)
        self.layout.addWidget(self.language_combo)

        self.voice_label = QtWidgets.QLabel("Select Voice:")
        self.layout.addWidget(self.voice_label)
        self.voice_combo = QtWidgets.QComboBox()
        self.voice_combo.addItems(["male", "female"])
        self.voice_combo.currentTextChanged.connect(self.change_voice_gender)
        self.layout.addWidget(self.voice_combo)

        self.mode_label = QtWidgets.QLabel("Select Mode:")
        self.layout.addWidget(self.mode_label)
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["speaking", "text", "reading"])
        self.mode_combo.currentTextChanged.connect(self.switch_mode)
        self.layout.addWidget(self.mode_combo)

        self.input_text = QtWidgets.QLineEdit()
        self.layout.addWidget(self.input_text)
        self.submit_button = QtWidgets.QPushButton("Submit")
        self.submit_button.clicked.connect(self.process_text)
        self.layout.addWidget(self.submit_button)

        self.result_label = QtWidgets.QLabel("Result:")
        self.layout.addWidget(self.result_label)
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        self.setLayout(self.layout)

    def switch_mode(self, mode):
        self.mode = mode

    def change_voice_gender(self, gender):
        self.selected_voice_gender = gender
        self.selected_voice = voices[self.selected_language][self.selected_voice_gender]

    def change_language(self, language):
        self.selected_language = language
        self.selected_voice = voices[self.selected_language][self.selected_voice_gender]

    def process_text(self):
        text = self.input_text.text()
        if text:
            if self.mode == "reading":
                asyncio.run(self.speak_edge_tts(text))
            else:
                response = self.get_ai_response(text)
                self.result_text.setPlainText(response)
                asyncio.run(self.speak_edge_tts(response))

    def get_ai_response(self, text):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": text}]
            )
            return response["choices"][0]["message"]["content"]
        except:
            return "Kechirasiz, hozir javob bera olmayman."

    async def speak_edge_tts(self, text):
        if self.selected_language == "uz":
            text = text.replace("-", "iinchi")  # Uzbek tilida "-" ni "chi" deb o'qish

        output_file = "output.mp3"
        try:
            communicate = edge_tts.Communicate(text, self.selected_voice)
            await communicate.save(output_file)
            self.play_audio(output_file)
        except Exception as e:
            print(f"TTS xatolik: {e}")

    def play_audio(self, file):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove(file)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = VoiceAssistantApp()
    window.show()
    app.exec_()
