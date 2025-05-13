import json, pyaudio
import openai
import os
import speech_recognition as sr
import pyttsx3
import pygame
import time
import serial
from vosk import Model,KaldiRecognizer
model = Model('vosk-model-small-ru-0.4')
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

pygame.mixer.init()
pygame.init()

tts = pyttsx3.init()

ser = serial.Serial('COM4', 9600, timeout=0.1)

OPENAI_API_KEY = "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"  # Не забудьте указать свой API ключ OpenAI

engine = pyttsx3.init()
engine.setProperty('rate', 160)
stream.start_stream()
phrases = {
    1: "Специализированная школа-лицей-интернат «Информационных технологий» открыла свои двери в две тысячи семнадцатом году. Учебное заведение расположено по адресу ул.Колодезная, 9. Год постройки здания 1958 год, проектная мощность 250 человек. Лицей имеет естественно-математическое направления и специализируется на информационных технологиях: робототехники, программировании, сетевых технологиях, трид моделировании, создании компьютерных игр. профилирующими предметами являются: физика, математика и информатика.",
    2: "Отемисова Асемгуль Каиртаевна, учитель казахского языка и литературы, кабинет двести тринадцатый, на втором этаже",
    3: "Кауров Станислав Сергеевич,учитель русского языка и литературы,кабинет 211,на втором этаже",
    4: "Айдарбеков Алтынбек Кабдрашевич,учитель физики,кабинет 202,на втором этаже ",
    5: "Расписание на понедельник",
    6: "Расписание на среду",
    7: "Меня создали в рамках соревнования Робокап в Нидерланды 2024",
    10: "сейчас мне дарят вторую жизнь в виде робота-гида для образовательных учреждений,ученики айти школы Сейфуллина Ясмин и Кадырганбек Рауан",
    8: "Более полную информацию о поступлении в школу, вы можете узнать на сайте школы.  Адрес сайта школы http:// айтилицеум точка кейзет ",
    9: "Манапова Айгуль Алихановна, дни приема посетителей среда с 14 до 17 часов, телефон 87021486610",
    11: "Здравствуйте!Я дерево гид. Спрашивайте что угодно!",
    12: "Ркнп 2025 проводится в городе Актобе,есть секции по общеобразовательным предметам,такие как математика,информатика,прикладная математика,химия,биология и так далее,в данный момент я являюсь проектом с исскуственным интеллектом для образовательных учреждениях",
    13: "Актобе я люблю тебя",
}   
def listen():
    while True:
       data = stream.read(4000, exception_on_overflow=False)
       if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']

def load_information(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Файл информации не найден."

def ask_gpt(question, knowledge, language):
    openai.api_key = OPENAI_API_KEY
    
    if language == "ru":
        prompt = f"""
        Ты - умный анализатор текста, а также робот-гид. У тебя есть ТОЛЬКО этот документ:

        {knowledge}

        Твоя задача:
            1. Найти ответ в тексте, даже если он написан другими словами или синонимами.
            2. Думать логически: например, если вопрос "Кто руководит школой?", а в тексте "Директор - Айгуль Манапова", значит, это ответ.
            3. Не придумывать! Если  в файле ответа нет, напиши информацию сам!"
            4. Если есть число, отвечай письменно
            5. если учителей по предмету несколько говори всех учителей, которые преподают этот предмет
            6. Тщательно анализируй текст, учителей не путай
            7. Ты должен найти только нужного учителя, если по предмету учителей несколько - перечисли их всех
        Вопрос: {question}
        """
    else:
        prompt = f"""
        Сен ақылды мәтін талдаушысысың және ақпараттық көмекшісің. Сенде ТЕК осы құжат бар:

        {knowledge}

        Міндеттерің:
            1. Жауапты мәтіннен табыңыз, тіпті ол басқа сөздермен немесе синонимдермен жазылған болса да.
            2. Логикалық ойлау: мысалы, егер сұрақ " мектепті кім басқарады?", ал "Директор - Айгүл Манапова" мәтінінде бұл жауап.
            3. Ойланбаңыз! Егер файлда жауап болмаса, ақпаратты өзіңіз жазыңыз!"
            4. Егер сан болса, жазбаша жауап беріңіз
            5. егер пән мұғалімдері бірнеше болса сөйлеңіз осы пәнді оқытатын барлық мұғалімдер
            6. Мәтінді мұқият талдаңыз, мұғалімдерді шатастырмаңыз
        
        Сұрақ: {question}
        """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

def show_image_while_speaking(image_paths, text, language):
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Просмотр изображений")
    
    for image_path in image_paths:
        try:
            image = pygame.image.load(image_path)
            screen.blit(pygame.transform.scale(image, screen.get_size()), (0, 0))
            pygame.display.flip()
        except FileNotFoundError:
            print(f"Изображение {image_path} не найдено.")
    
#    pygame.display.quit()

def show_image_while_speaking2(image_paths, text, language):
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Просмотр изображений")
    
    for image_path in image_paths:
        try:
            image = pygame.image.load(image_path)
            screen.blit(pygame.transform.scale(image, screen.get_size()), (0, 0))
            pygame.display.flip()
        except FileNotFoundError:
            print(f"Изображение {image_path} не найдено.")
    

def extract_subject(question):
    subjects = [
        "математики", "физики", "химии", "биологии", "истории", 
        "географии", "литературы", "информатики", "английского", 
        "русскому", "казахского", "робототехники", "пятцицу", "расписание",
        "вторник", "среду", "четверг", "понедельник", "пятого а", "пятого в", "шестого а", "шестого в",
        "седьмого а" , "седьмого в" , "восьмого а"
    ]
    for subject in subjects:
        if subject in question:
            return subject
    return None

def check_for_images(question, language, answer):
    teacher_keywords = ["учитель", "преподаватель", "преподает", "расписание", "куратор", "директор"]
    schedule_keywords = ["уроки", "занятия"]

    folder = r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\teachers"
    '''
    if any(word in question for word in schedule_keywords):
        schedule_path = os.path.join("RKNP", "vosk", "schedule.jpg")
        if os.path.exists(schedule_path):
            show_image_while_speaking([schedule_path], answer, language)
        else:
            print("Файл расписания не найден.")
        return
    '''
    if any(word in question for word in teacher_keywords):
        subject = extract_subject(question)
        if not subject:
            print("Не удалось определить предмет.")
            return
        if os.path.exists(folder):
            image_paths = [os.path.join(folder, f) for f in os.listdir(folder) if subject.lower() in f.lower()]
            if image_paths:
                show_image_while_speaking(image_paths, answer, language)
            else:
                print(f"Фотографии учителя по предмету '{subject}' не найдены.")
        else:
            print(f"Папка с фотографиями не найдена: {folder}")

            

def speak(text, language):
    if language == "kk":
        engine.setProperty('voice', 'Kazakh')
    else:
        engine.setProperty('voice', 'russian')
    ser.write(b'bruhh')
    engine.say(text)
    engine.runAndWait()
    ser.write(b'brr')

   
    
def recognize_speech(language):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Говорите..." if language == "ru" else "Айтыңыз...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=9)
            text = recognizer.recognize_google(audio, language="ru-RU" if language == "ru" else "kk-KZ")
            print(f"Вы сказали: {text}" if language == "ru" else f"Сіз айттыңыз: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Не удалось распознать речь." if language == "ru" else "Дыбысты тану мүмкін болмады.")
            return None
        except sr.RequestError:
            print("Ошибка соединения с Google API." if language == "ru" else "Google API-мен байланыс қатесі.")
            return None

def choose_language():
    while True:
        ser.write(b'bruhh')
        print("Выберите язык: русский или казахский")
        engine.say("Выберите язык: русский или казахский")
        engine.runAndWait()
        ser.write(b'brr')
        for text in listen():
          question = text 

          if text in ["русский", "ру", "russian", "на русском", "русском"]:
              engine.say("Вы выбрали русский язык")
              engine.runAndWait()
              return "ru"
          elif text in ["казахский", "каз", "казакша", "kazakh", "на казахском", "казахском", "қазақ", "қазақша"]:
              engine.say("Сіз қазақ тілін таңдадыңыз")
              engine.runAndWait()
              return "kk"
          else:
              print("Не распознано. Попробуйте снова.")
              speak("Не распознано. Попробуйте снова.", "ru")
              print(text)
              return "ru"

def main():
    for text in listen():
        print(text)
        question = text 
        file_path = "school3.txt" 
        knowledge = load_information(file_path)
        
        print("Задайте вопрос или скажите 'выход', чтобы выйти.")
#        question = recognize_speech(language)
        if question is None:
            continue
        if question in ["стоп", "выход", "завершить", "тоқта", "шығу", "аяқтау","до свидания", "пока"]:
            print("Завершаю работу. До свидания!")
            ser.write(b'bruhh')
            speak("Завершаю работу. До свидания!")
            ser.write(b'brr')
            break
#        answer = ask_gpt(question, knowledge, "ru")
        if 'расскажи о школе' in text:
          ser.write(b'bruhh')
          tts.say(phrases[1])
          tts.runAndWait()
          ser.write(b'brr')
        elif 'кто тебя создал' in text:
            ser.write(b'bruhh')
            folder = r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\img\monday.JPG"
            show_image(r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\teachers\учителя химии.png")  # Замените на путь к вашему изображению
            tts.say(phrases[7])
            tts.runAndWait()
            pygame.time.wait(1500)
            show_image(r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\teachers\karaganda.JPG")  # Замените на путь к вашему изображению
            tts.say(phrases[10])
            tts.runAndWait()
            ser.write(b'brr')
        elif "расписание на понедельник" in text:
            ser.write(b'bruhh')
            folder = r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\img\monday.JPG"
            if os.path.exists(folder):
                print(folder)
                image_paths = [os.path.join(folder, r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\img\monday.JPG")]
                show_image_while_speaking2(image_paths, phrases[5], "ru")
                speak(text, "ru")
        elif "спасибо" in text:
             ser.write(b'bruhh')
             tts.say("хорошо, закрываю окно")
             tts.runAndWait()
             pygame.display.quit()
             ser.write(b'brr')
        elif "республиканский конкурс в актобе" in text:
            
            ser.write(b'bruhh')
            
            folder = r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\img\aktobe.jpg"
            if os.path.exists(folder):
                print(folder)
                image_paths = [os.path.join(folder, r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\img\aktobe.jpg")]
                show_image_while_speaking2(image_paths, tts.say('Ркнп 2025 проводится в городе Актобе, есть секции по общеобразовательным предметам, такие как математика, информатика, прикладная математика, химия, биология и так далее, в данный момент я являюсь проектом с исскуственным интеллектом для образовательных учреждениях",'), "ru")
                tts.runAndWait ()
                pygame.time.wait(1500)
                image_paths = [os.path.join(folder, r"C:\Users\ind.ivi.ddd\Desktop\RKNP\vosk\img\aktobelove.jpg")]
                show_image_while_speaking2(image_paths, tts.say('я люблю тебя Актобе'), "ru")
                tts.runAndWait()
            
                                                                
                         
                
        else:  
            answer =ask_gpt(question, knowledge, "ru")
#           answers=answer
            check_for_images(question, "ru", answer )
            print(answer, "ru")
            speak(answer, "ru")

        
if __name__ == "__main__":
    main()
