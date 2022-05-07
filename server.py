# встроенные биб-ки
import datetime
import os
import random

# фласк
from flask import Flask, render_template, request
from flask import redirect
import flask_login
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf import FlaskForm, RecaptchaField

# формы
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# другие библиотеки
import yadisk
from pathlib import Path
import threading
from threading import Timer

# из своих файлов
from data import db_session
from data import posts
from data.posts import User
from data.keys import KeyForReg
from posting import create_post
from draw_post_tree import get_format_posts, delete_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'in_fact_we_are_not_powerless_but_weak-willed__will_will_make_any_choice_right'

app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfrPIEfAAAAAN1AhaD6c19E7kJzP2ylCtsYeg9X'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfrPIEfAAAAAI6JhObHV61OybpGyk62mrJ2oqK4'

boards = [["разное", "/abu", "/b", "/media", "/r", "/soc"],
          ["тематика", "/au", "/bi", "/biz", "/bo", "/cc"],
          ["творчество", "/de", "/di", "/diy", "/mus", "/p", "/pa"],
          ["политикка", "/hry", "/news", "/po"]]

hidden_posts = dict()
buttons = dict()

filepath = "static/images/uploads/"

login_manager = LoginManager()
login_manager.init_app(app)

ycloud_manager = yadisk.YaDisk(token="AQAAAABgRHWRAAfWz0e6ldvRxkQerikLrbA9aG8")

# TODO: перед деплоем отключить:
local_mode =True  # когда включен этот режим,
# отключается капча и синхронизация картинок, по другому генерируется время поста

update_time = int(15 * 60)  # промежуток времени в секундах, через который делается проверка бд на актуальность
db_is_outdated = False  # флаг, является ли бд в облаке устаревшей
timer_is_sleep = False  # флаг, заснул ли таймер
# он засыпает, когда никто ничего не постит в течение update_time
# он работает, когда есть хоть 1 пост в течение update_time
# он просыпается, когда появился пост после того, как таймер заснул
enable_imagecloud_logs = True
if local_mode:
    enable_captcha = False
    enable_image_sync_with_cloud = False
    enable_download_base = False
else:
    enable_captcha = True
    enable_image_sync_with_cloud = True
    enable_download_base = True

# получение списка фалов в облаке и списка имеющихся файлов
# (это нужно чтобы пока картинки будут качаться, сервер мог работать:)
# отображение картинок:
#   если файл есть на сервере                           отобразить этот файл
#   если файла нет на сервере, но он есть в облаке      отобразить картинку-сообщение, что файлы еще грузятся
#   если файла нет нигде                                отобразить юрл с ошибкой
cloud_files = []
local_files = []


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class BlessForm(FlaskForm):
    submit = SubmitField('благославить пост')


class LoginForm(FlaskForm):
    nickname = StringField('ваш никнэйм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    nickname = StringField('ваш никнэйм', validators=[DataRequired()])
    key_for_reg = StringField('введите пригласительный инвайт ключ', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class AnswerForm(FlaskForm):
    # title = StringField('введите заголовок', validators=[DataRequired()])
    # messenge = StringField('введите ваше сообщение', validators=[DataRequired()])

    if enable_captcha:
        recaptcha = RecaptchaField()
    submit = SubmitField('запостить')


class AnswerButton(FlaskForm):
    submit = SubmitField('ответить')


class CloseButton(FlaskForm):
    submit2 = SubmitField('скрыть/открыть ответы')


@app.route("/")
def index():
    # create_folders(boards,filepath)
    folder = Path("static/images/main_gifs")
    max_folder_id = len(list(folder.iterdir())) - 1
    gifs_ids = []
    i = 0
    while i < 4:
        number = random.randint(0, max_folder_id)
        if number not in gifs_ids:
            gifs_ids.append(number)
            i += 1
    gifs_ids2 = []
    i = 0
    while i < 4:
        number = random.randint(0, max_folder_id)
        if number not in gifs_ids2 and number not in gifs_ids:
            gifs_ids2.append(number)
            i += 1

    count_posts = {}
    for line in boards:
        for db_section in line[1:]:
            db_sess = db_session.create_session()
            a = getattr(posts, db_section[1:])
            count = len(list(db_sess.query(a).all()))
            count_posts[db_section] = count

    return render_template("home.html", boards=boards, gifs_ids=gifs_ids, gifs_ids2=gifs_ids2, count_posts=count_posts)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(KeyForReg).filter(KeyForReg.key == form.key_for_reg.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="неверный инвайт ключ")
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.nickname = form.nickname.data
        user.set_password(form.password.data)
        user.verifyed = False
        db_sess.add(user)
        db_sess.commit()

        key_field = db_sess.query(KeyForReg).filter(KeyForReg.key == form.key_for_reg.data).first()
        key_field.is_active = 0
        db_sess.add(key_field)
        db_sess.commit()

        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/messenge_to/<section>/<int:reply_to_id>", methods=['GET', 'POST'])
def create_messenge(section, reply_to_id):
    global db_is_outdated, timer_is_sleep
    form = AnswerForm()

    if form.validate_on_submit():

        # messenge = form.messenge._value()
        messenge = request.form["messenge"]
        title = request.form["title"]
        file = request.files["file_upload"]
        file_href = request.form["file_href"]
        id = len(get_format_posts(section, buttons))
        if file:
            filename = f"{filepath}{section}/file{id}.{file.filename.split('.')[-1]}"
            file.save(filename)
        elif file_href:
            filename = file_href
        else:
            filename = ""
            # print("aboba")
        # title = form.title._value()

        time = datetime.datetime.now()
        if not local_mode:
            time += datetime.timedelta(hours=5)

        create_post(section, title, messenge, reply_to_id, hidden_posts, time, filename)

        # format_posts=get_format_posts(section,buttons)
        # hide_posts(id,id,format_posts)

        db_is_outdated = True
        if timer_is_sleep:
            timer_is_sleep = False
            t = Timer(update_time, check_bd)
            t.start()

        return redirect(f'/{section}')
    return render_template("messenge_form.html", form=form, to_id=reply_to_id)


def hide_posts(beggin_beggin_id, begin_id, posts):
    for i in posts:
        if i[1].reply_to_id == begin_id:
            hidden_posts[beggin_beggin_id].append(i[1].id)
            hide_posts(beggin_beggin_id, i[1].id, posts)
    pass


def show_posts(begin_id):
    del (hidden_posts[begin_id])


@app.route("/<db_section>", methods=['GET', 'POST'])
def index2(db_section):
    global buttons, counter
    global cloud_files, local_files

    # if not len(hidden_posts):
    if db_section == 'None':
        # print("flask is stupid shit for dumbasses")
        return ""

    delete_data()
    bless = BlessForm()
    if bless.validate_on_submit():
        try:
            index = int(request.form["index2"])
            name = request.form["name"]

            from data import posts
            Posts = getattr(posts, db_section)
            db_sess = db_session.create_session()
            for i in db_sess.query(Posts).filter(Posts.id == index):
                post = i
            if post.blessing != None:
                post.blessing = post.blessing + name
            else:
                post.blessing = name + " "
            db_sess.commit()

        except:
            pass

    format_posts = get_format_posts(db_section, buttons)[::-1]

    i = 0
    post_pos = 0
    zero_pos = []
    # сортировка постов, чтобы ответы были под постами
    # сначала заголовки
    while i < len(format_posts):
        if format_posts[i][1].reply_to_id == 0:
            if i != post_pos:
                format_posts.insert(post_pos, format_posts[i])
                del (format_posts[i + 1])
            post_pos = i + 1

        i += 1
    # теперь сами посты
    for i in range(len(format_posts)):
        if format_posts[i][1].reply_to_id == 0:
            zero_pos.append(i)
    zero_pos.append(len(format_posts) - 1)
    for i in range(len(zero_pos) - 1):
        # print(format_posts[zero_pos[i] + 1:zero_pos[i + 1]][::-1])
        format_posts[zero_pos[i] + 1:zero_pos[i + 1]] = format_posts[zero_pos[i] + 1:zero_pos[i + 1]][::-1]

    # ооо сейчас будут говнокостыли: структура поста будет переделана
    # из    (отступ, пост, переменная_отвечающая_за_скрытие)
    # в     [отступ, пост, переменная_отвечающая_за_скрытие, список_id_постов-ответов]
    # апдейт: после этого преобразования все слетело [к черту],
    # так что будут существовать 2 версии: format_posts_with_reply и format_post (с ссылками на ответы и без)
    last_main_post_id = 0
    format_posts_with_reply = []
    for i, post in enumerate(format_posts):
        if post[0] == 0:  # если отступ = 0, не добавляем этот пост в список
            continue
        format_posts_with_reply.append(list(format_posts[i]))
        format_posts_with_reply[i].append([])
        if post[0] == 1:
            last_main_post_id = i
        else:
            format_posts_with_reply[last_main_post_id][3].append(i)

    # если файла нет на сервере, но он есть в облаке, то картинка заменяется на картинку-сообщение о том,
    # что картинки сейчас качаются
    # структура меняется на
    # [отступ, пост, переменная_отвечающая_за_скрытие, список_id_постов-ответов, bool:есть_ли_картинка]
    update_local_files()
    for i, post in enumerate(format_posts_with_reply):
        format_posts_with_reply[i].append(True)
        path = post[1].files
        if path is None:
            continue
        if not path.startswith('static/images/uploads/'):
            continue
        path = path[len('static/images/uploads'):]
        if (path not in local_files) and (path in cloud_files):
            # format_posts_with_reply[i][1].files = 'static/images/downloading_message.png'
            format_posts_with_reply[i][4] = False


    form2 = CloseButton()

    if form2.validate_on_submit():
        try:
            index = int(request.form["index"])
            if format_posts[index][1].id not in hidden_posts.keys():
                hidden_posts[format_posts[index][1].id] = []
                format_posts[index] = (format_posts[index][0], format_posts[index][1], 2)
                # hidden_posts.append(format_posts[index][1].id)
                buttons[format_posts[index][1].id] = 2
                hide_posts(format_posts[index][1].id, format_posts[index][1].id, format_posts)
            else:
                format_posts[index] = (format_posts[index][0], format_posts[index][1], 1)
                buttons[format_posts[index][1].id] = 1
                show_posts(format_posts[index][1].id)
        except:
            pass
    return render_template("main.html", format_posts_with_reply=format_posts_with_reply,
                           section=db_section, form2=form2, hidden_posts=hidden_posts, bless=bless)

    # print(type(format_posts[index][1]))
    # этот ретерн можно не писать
    # return redirect(f'/messenge_to/{db_section}/{id}')
    # print(format_posts)


def upload_dir(path, to_dir, deep=0):
    if deep == 0:
        if not ycloud_manager.exists(to_dir):
            ycloud_manager.mkdir(to_dir)
    for obj in os.listdir(path=path):
        local_obj_path = path + '/' + obj
        cloud_obj_path = to_dir + '/' + obj
        if '.' not in obj:
            if enable_imagecloud_logs:
                print('\t' * deep + obj + '/')
            if not ycloud_manager.exists(cloud_obj_path):
                ycloud_manager.mkdir(cloud_obj_path)
            upload_dir(path=local_obj_path, to_dir=cloud_obj_path, deep=deep + 1)
        elif '.' in obj:
            if enable_imagecloud_logs:
                print('\t' * deep + obj)
            if not ycloud_manager.exists(cloud_obj_path):
                ycloud_manager.upload(local_obj_path, cloud_obj_path)


def download_dir(path, to_dir, deep=0):
    if deep == 0:
        if not os.path.exists(to_dir):
            os.mkdir(to_dir)

    for obj in ycloud_manager.listdir(path=path):
        cloud_obj_path = path + '/' + obj.name
        local_obj_path = to_dir + '/' + obj.name
        if obj.type == 'dir':
            if enable_imagecloud_logs:
                print('\t' * deep + obj.name + '/')
            if not os.path.exists(local_obj_path):
                os.mkdir(local_obj_path)
            download_dir(path=cloud_obj_path, to_dir=local_obj_path, deep=deep + 1)
        elif obj.type == 'file':
            if enable_imagecloud_logs:
                print('\t' * deep + obj.name, end='')
                print(' ' * (30 - len('\t' * deep + obj.name)), end='')
            if not os.path.exists(local_obj_path):
                print('downloading...')
                ycloud_manager.download(cloud_obj_path, local_obj_path)
            else:
                print()


def download_bd(enable_download_image=True, enable_download_base=True):
    if enable_download_base:
        print('загрузка бд...')
        ycloud_manager.download("/cloud/borda.db", "db/borda.db")
        print('загрузка бд завершена')

    if enable_download_image:
        if enable_imagecloud_logs:
            print('загрузка картинок из облака...')
        download_dir('cloud/images', 'static/images/uploads')
        if enable_imagecloud_logs:
            print('загрузка картинок из облака завершена')


def upload_bd():
    if ycloud_manager.exists('/cloud/borda.db'):
        ycloud_manager.remove("/cloud/borda.db", permanently=True)

    print('отгрузка бд на облако...')
    ycloud_manager.upload("db/borda.db", "/cloud/borda.db")
    print('отгрузка бд завершена')

    if enable_imagecloud_logs:
        print('отгрузка картинок на облако...')
    upload_dir('static/images/uploads', 'cloud/images')
    if enable_imagecloud_logs:
        print('отгрузка на облако кончилась')

    update_cloud_files()


def check_bd():
    """проверка бд на актуальность"""
    global db_is_outdated, timer_is_sleep, update_time
    if db_is_outdated:
        upload_bd()
        db_is_outdated = False
        timer_is_sleep = False
        t = Timer(update_time, check_bd)
        t.start()
    else:
        timer_is_sleep = True


@app.route('/gen_key')
def gen_key():
    n_keys_for_one_user = 6

    letters = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    n_block = 4
    len_block = 4
    keys = []

    db_sess = db_session.create_session()
    if flask_login.current_user.is_authenticated:
        user = db_sess.query(User).filter(User.id == flask_login.current_user.get_id()).first()
        if not user.keys_already_gen:
            for i in range(n_keys_for_one_user):
                key = '-'.join(''.join(random.choice(letters) for i in range(len_block)) for j in range(n_block))
                key_field = KeyForReg()
                key_field.key = key
                key_field.user_id = flask_login.current_user.get_id()
                db_sess.add(key_field)
            db_sess.commit()

            user.keys_already_gen = 1
            db_sess.add(user)
            db_sess.commit()

        keys = list(db_sess.query(KeyForReg).filter(KeyForReg.user_id == user.id))

    return render_template("gen_key.html", keys=keys)


def update_cloud_files():
    global cloud_files
    cloud_files = []
    a = list(ycloud_manager.get_files())
    for i in a:
        if i.path.startswith('disk:/cloud/images/'):
            path = i.path[len('disk:/cloud/images'):]
            cloud_files.append(path)


def update_local_files():
    global local_files
    local_files = []
    b = list(os.walk('static/images/uploads'))
    for i in b[1:]:
        razdel = i[0][len('static/images/uploads') + 1:]
        for j in i[2]:
            path = '/' + razdel + '/' + j
            local_files.append(path)


def compare_local_and_cloud_files():
    global cloud_files
    global local_files
    print('сравнение фалов в облаке и локальных')
    print('облако', ' ' * (30 - len('облако')), 'локалка', sep='')
    for path in cloud_files:
        print(path, end='')
        print(' ' * (30 - len(path)), end='')
        if path in local_files:
            print(path)
        else:
            print('-')
    print('конец сравнения')



def main():
    db_session.global_init("db/borda.db")
    # for self
    # app.run(port=8080, host='127.0.0.1')
    # for internet

    update_cloud_files()
    update_local_files()

    # проверка файлов (кажется на хероку неправильно определяются локальные файлы)
    compare_local_and_cloud_files()

    # надеюсь, что когда хироку уходит в ребут,
    # то он начинает работать отсюда
    download_thread = threading.Thread(target=download_bd,
                                       kwargs={'enable_download_image': enable_image_sync_with_cloud,
                                               'enable_download_base': enable_download_base})
    download_thread.start()
    # download_bd(enable_download_image=enable_image_sync_with_cloud, enable_download_base=enable_download_base)
    check_bd()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
