from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
import string
import re
import pickle
import pathlib
from sklearn.linear_model import SGDClassifier
from imblearn.pipeline import Pipeline


root = Tk()
root.title("Проверка pdf-файла на соответствие эталонному названию")
root.geometry("450x200")

root.grid_rowconfigure(index=0, weight=1)
root.grid_columnconfigure(index=0, weight=1)
root.grid_columnconfigure(index=1, weight=1)
nltk.download('stopwords')
russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['Нет данных', 'Нет', 'Не требуется'])

def clean_data(line):

    tokens = str(line)
    tokens = [re.sub('<[^>]+>', '', token).strip(string.punctuation) for token in tokens.split()]
    line = " ".join(tokens)
    return line

def preprocess_data(text):

    tokens = str(text)
    tokens = [token for token in tokens.split() if token not in russian_stopwords\

              and token.isalpha()\
              and len(token)>=3 ]
    text = " ".join(tokens)
    return text
data = []
pdf_file = []
def open_file():
    global data
    global pdf_file
    filepath = filedialog.askopenfilename()
    if filepath != "":
        if filepath[-4:] == '.pdf':
            reader = PdfReader(filepath)
            if len(reader.pages) > 1:
                page = reader.pages[0]
                pdf_file.append(reader.pages)
                data.extend(preprocess_data(clean_data(page.extract_text())).split('\n'))
            else:
                messagebox.showerror('Ошибка', 'pdf-файл содержит только одну страницу с таблицами')
        else:
            messagebox.showerror('Ошибка', 'файл не формате pdf')

    return data

DATA_DIR = pathlib.Path(".")
MODEL_FILE = pathlib.Path(__file__).parent.joinpath('model.pkl')

with open(MODEL_FILE, 'rb') as file:
    model = pickle.load(file)
message = ""
def check():
    global data
    global pdf_file
    global message
    messagebox.showinfo(title="Предупреждение", message="Не закрывайте программу, проверка может занять несколько минут")
    title = ''.join(model.predict(data))

    for pdf in pdf_file:
        for current_page in range(len(pdf)):
            text = pdf[current_page].extract_text()
            res = preprocess_data(clean_data(text)).lower().find(preprocess_data(clean_data(title)).lower()[:10])
            if res > 0:
                message += '\n' + f"Стоит обратить внимание на то,        как написано название на странице {current_page}"
    return messagebox.showinfo(title="Информация", message=message)

# сохраняем текст из текстового поля в файл
def save_file():
    global message
    filepath = filedialog.asksaveasfilename(defaultextension=".txt")
    if filepath != "":

        with open(filepath, "w") as file:
            file.write(message)

open_button = ttk.Button(text="Открыть файл", command=open_file)
open_button.grid(column=0, row=1, sticky=NSEW, padx=10)

check_button = ttk.Button(text="Проверить", command=check)
check_button.grid(column=1, row=1, sticky=NSEW, padx=10)

save_button = ttk.Button(text="Сохранить файл", command=save_file)
save_button.grid(column=2, row=1, sticky=NSEW, padx=10)






root.mainloop()