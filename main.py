import os
import queue
import threading
import time
from tkinter import Tk, Button, Label, messagebox
import sounddevice as sd
import soundfile as sf
import speech_recognition
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound


class VoiceQnA:
    def __init__(self):
        # Create a queue to contain the audio data
        self.q = queue.Queue()
        self.status_text = "Answer not recorded."
        self.next_btn_text = 'Next'
        self.recorded_text = ''
        self.recorded_text_writing = False
        self.recording_btn_text = 'Record Answer'
        # Declare variables and initialise them
        self.next_btn_enable = False
        self.recording = False
        self.file_exists = False
        # super(VoiceQnA, self).__init__()
        self.q_no = 0
        self.data_size = len(all_questions)
        self.dynamic_elements()
        title = Label(gui, text="Voice Question & Answer",
                      width=50, bg="green", fg="white", font=("ariel", 20, "bold"))
        title.place(x=0, y=2)

    def text_to_speech(self, _text):
        language = 'en'
        myObj = gTTS(text=_text, lang=language, slow=False)
        myObj.save("temp_audio.mp3")
        playsound("temp_audio.mp3")
        try:
            os.remove("temp_audio.mp3")
        except:
            pass

    def speech_to_text(self, _filename):
        r = sr.Recognizer()
        try:
            with sr.AudioFile(_filename) as source:
                # listen for the data (load audio to memory)
                audio_data = r.record(source)
                # recognize (convert from speech to text)
                text = r.recognize_google(audio_data)
            return text
        except ValueError:
            return ""

    # Fit data into queue
    def callback(self, indata, frames, time, status):
        self.q.put(indata.copy())

    # Functions to play, stop and record audio
    # The recording is done as a thread to prevent it being the main process
    def threading_rec(self, x, _object_list):
        if x == 0:
            t0 = threading.Thread(target=self.text_to_speech, args=[all_questions[self.q_no]])
            t0.start()
        elif x == 1:
            self.recording_btn_text = 'Recording..'
            self.dynamic_elements()
            # If recording is selected, then the thread is activated
            t1 = threading.Thread(target=self.record_audio)
            t1.start()
        elif x == 2:
            # To stop, set the flag to false
            self.recording_btn_text = 'Record Answer'
            self.dynamic_elements()
            global recording
            recording = False
            # check if speech contain text
            try:
                self.recorded_text = self.speech_to_text("trial.wav")
                if len(self.recorded_text)> 0:  # second confirmation of text
                    self.status_text = "Answer received."
                    self.next_btn_enable = True
                    self.dynamic_elements()
                else:
                    self.next_btn_enable = False
                    self.status_text = "Didn't hear anything. Please try again."
                    self.dynamic_elements()
            except speech_recognition.UnknownValueError:
                self.next_btn_enable = False
                self.status_text = "Didn't hear anything. Please try again."
                self.dynamic_elements()
        elif x == 3:
            # To play a recording, it must exist.
            if file_exists:
                # Read the recording if it exists and play it
                data, fs = sf.read("trial.wav", dtype='float32')
                sd.play(data, fs)
                sd.wait()
            else:
                # Display and error if none is found
                messagebox.showerror(message="Some error occured")
        elif x == 4:
            if self.q_no + 1 == self.data_size:
                os.remove("trial.wav")
                if not self.recorded_text_writing:
                    self.recorded_text_writing = True
                    with open('answers.txt', 'w') as f:
                        f.truncate()
                        f.write(self.recorded_text + '\n')
                else:
                    with open('answers.txt', 'a+') as f:
                        f.write(self.recorded_text+'\n')
                gui.destroy()
            else:
                # shows the next question and all related buttons
                if not self.recorded_text_writing:
                    self.recorded_text_writing = True
                    with open('answers.txt', 'w') as f:
                        f.truncate()
                        f.write(self.recorded_text + '\n')
                else:
                    with open('answers.txt', 'a+') as f:
                        f.write(self.recorded_text+'\n')
                self.q_no += 1
                self.next_btn_enable = False
                self.status_text = "Answer not recorded."
                if all_questions[self.q_no] == all_questions[-1]:
                    self.next_btn_text = "Finish"
                self.dynamic_elements()
        elif x == 5:
            try:
                os.remove("trial.wav")
            except:
                pass
            gui.destroy()

    # Recording function
    def record_audio(self):
        # Declare global variables
        global recording
        # Set to True to record
        recording = True
        global file_exists
        # Create a file to save the audio
        # messagebox.showinfo(message="Recording Audio. Speak into the mic")
        with sf.SoundFile("trial.wav", mode='w', samplerate=44100,
                          channels=2) as file:
            # Create an input stream to record audio without a preset time
            with sd.InputStream(samplerate=44100, channels=2, callback=self.callback):
                while recording:
                    # Set the variable to True to allow playing the audio later
                    file_exists = True
                    # write into file
                    file.write(self.q.get())

    def dynamic_elements(self):
        quit_button = Button(gui, text="Quit", command=gui.destroy, width=5, bg="black", fg="white", font=("ariel", 16, " bold"))
        quit_button.place(x=700, y=50)

        question_number = Label(gui, text="Question - " + str(self.q_no + 1), width=16, font=('ariel', 16, 'bold'), anchor='w')
        question_number.place(x=50, y=50)

        play_question = Button(gui, text="Play Question", width=13, font=("ariel", 16, "bold"), bg = "#6CD300")
        play_question.place(x=70, y=100)

        record_btn = Button(gui, text=self.recording_btn_text, width=13, font=("ariel", 16, "bold"), bg= "#FBBD01")
        record_btn.place(x=70, y=200)

        stop_btn = Button(gui, text="Stop Recording", width=13, font=("ariel", 16, "bold"), bg= "#eb4132")
        stop_btn.place(x=300, y=200)

        answer_status = Label(gui, text=self.status_text, width=60, font=('ariel', 16, 'bold'), anchor='w')
        answer_status.place(x=70, y=300)

        if self.next_btn_enable:
            next_button = Button(gui, text=self.next_btn_text, width=10, font=("ariel", 16, "bold"), bg="blue", fg="white")
            next_button.place(x=350, y=380)
            play_btn = Button(gui, text="Play Answer", width=13, font=("ariel", 16, "bold"), bg="#4086f4")
            play_btn.place(x=550, y=200)
        else:
            next_button = Button(gui, text=self.next_btn_text, width=10, font=("ariel", 16, "bold"), bg="blue", fg="white", state = 'disabled')
            next_button.place(x=550, y=380)
            play_btn = Button(gui, text="Play Answer", width=13, font=("ariel", 16, "bold"), bg="#4086f4", state= 'disabled')
            play_btn.place(x=550, y=200)

        object_list = [play_question, record_btn, stop_btn, play_btn, next_button]
        play_question['command'] = lambda m=0: self.threading_rec(m, object_list)
        record_btn['command'] = lambda m=1: self.threading_rec(m, object_list)
        stop_btn['command'] = lambda m=2: self.threading_rec(m, object_list)
        play_btn['command'] = lambda m=3: self.threading_rec(m, object_list)
        next_button['command'] = lambda m=4: self.threading_rec(m, object_list)
        quit_button['command'] = lambda m=5: self.threading_rec(m, object_list)


gui = Tk()
gui.geometry("800x450")
gui.title("Voice Q&A")
gui.minsize(850, 450)
gui.maxsize(850, 450)
with open('question.txt') as f:
    all_questions = list(filter(None, f.read().splitlines()))

VoiceQnA = VoiceQnA()
gui.mainloop()
