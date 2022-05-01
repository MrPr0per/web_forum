# получить список всех файлов в облаке
# получить список всех файлов на сервере

# отображение картинок:
#   если файл есть на сервере                           отобразить этот файл
#   если файла нет на сервере, но он есть в облаке      отобразить картинку-сообщение, что файлы еще грузятся
#   если файла нет нигде                                отобразить юрл с ошибкой
#

# при запуске:
# запустить сервер
# в параллельном потоке запустить загрузку картинок

import yadisk
from pprint import pprint
import os
from flask import Flask
import time
import threading

app = Flask(__name__)

ycloud_manager = yadisk.YaDisk(token="AQAAAABgRHWRAAfWz0e6ldvRxkQerikLrbA9aG8")

uploaded_data = None


def count(n):
    global uploaded_data
    print(threading.current_thread().name)
    for i in range(n):
        print(i)
        time.sleep(1)
    print('готово')
    uploaded_data = '*картинка*'


@app.route('/')
@app.route('/index')
def index():
    global uploaded_data
    if uploaded_data:
        return f"загрузка завершена: {uploaded_data}"
    else:
        return 'загрузка...'


if __name__ == '__main__':
    thr2 = threading.Thread(target=count, kwargs={'n': 3})
    thr2.start()
    # app.run(port=8080, host='127.0.0.1')
    while True:
        input()
        thr2 = threading.Thread(target=count, kwargs={'n': 3})
        thr2.start()

