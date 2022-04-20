from flask import Flask, render_template, request

from data import db_session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired
from flask import redirect
from posting import create_post, create_folders
from draw_post_tree import get_format_posts, delete_data
import os
from flask_login import LoginManager, login_user, logout_user, login_required
from data.posts import User
import random
from pathlib import Path

import yadisk
from threading import Timer

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
develop_mode = False  # когда включен этот режим, отключается капча и синхронизация картинок

update_time = int(15 * 60)  # промежуток времени в секундах, через который делается проверка бд на актуальность
db_is_outdated = False  # флаг, является ли бд в облаке устаревшей
timer_is_sleep = False  # флаг, заснул ли таймер
# он засыпает, когда никто ничего не постит в течение update_time
# он работает, когда есть хоть 1 пост в течение update_time
# он просыпается, когда появился пост после того, как таймер заснул
enable_imagecloud_logs = True
if develop_mode:
    enable_captcha = False
    enable_image_sync_with_cloud = False
else:
    enable_captcha = True
    enable_image_sync_with_cloud = True


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class bless_form(FlaskForm):
    submit = SubmitField('благославить пост')


class LoginForm(FlaskForm):
    nickname = StringField('ваш никнэйм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    nickname = StringField('ваш никнэйм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class Answer_Form(FlaskForm):
    # title = StringField('введите заголовок', validators=[DataRequired()])
    # messenge = StringField('введите ваше сообщение', validators=[DataRequired()])

    if enable_captcha:
        recaptcha = RecaptchaField()
    submit = SubmitField('запостить')


class Answer_button(FlaskForm):
    submit = SubmitField('ответить')


class Close_button(FlaskForm):
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

    return render_template("home.html", boards=boards, gifs_ids=gifs_ids, gifs_ids2=gifs_ids2)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.nickname = form.nickname.data
        user.set_password(form.password.data)
        user.verifyed = False
        db_sess.add(user)
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
    form = Answer_Form()

    if form.validate_on_submit():

        # messenge = form.messenge._value()
        messenge = request.form["messenge"]
        title = request.form["title"]
        file = request.files["file_upload"]
        id = len(get_format_posts(section, buttons))
        if file:
            filename = f"{filepath}{section}/picture{id}.{file.filename.split('.')[1]}"
            file.save(filename)
        else:
            filename = ""
            # print("aboba")
        # title = form.title._value()

        create_post(section, title, messenge, reply_to_id, hidden_posts, filename)

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

    # if not len(hidden_posts):
    if db_section == 'None':
        # print("flask is stupid shit for dumbasses")
        return ""

    delete_data()
    bless = bless_form()
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

    form2 = Close_button()

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
    return render_template("main.html", format_posts=format_posts, section=db_section, form2=form2,
                           hidden_posts=hidden_posts, bless=bless)

    # print(type(format_posts[index][1]))
    # этот ретерн можно не писать
    # return redirect(f'/messenge_to/{db_section}/{id}')
    # print(format_posts)


def upload_dir(path, to_dir, deep=0):
    if deep == 0:
        if enable_imagecloud_logs:
            print('загрузка картинок на облако...')
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
    if deep == 0:
        if enable_imagecloud_logs:
            print('загрузка картинок на облако завершена')


def download_dir(path, to_dir, deep=0):
    if deep == 0:
        if enable_imagecloud_logs:
            print('загрузка картинок из облака...')
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
                print('\t' * deep + obj.name)
            if not os.path.exists(local_obj_path):
                ycloud_manager.download(cloud_obj_path, local_obj_path)
    if deep == 0:
        if enable_imagecloud_logs:
            print('загрузка картинок из облака завершена')


def download_bd(enable_download_image=True):
    ycloud_manager.download("/cloud/borda.db", "db/borda.db")
    if enable_download_image:
        download_dir('cloud/images', 'static/images/uploads')


def upload_bd():
    if enable_imagecloud_logs:
        print('произошло обновление')
    if ycloud_manager.exists('/cloud/borda.db'):
        ycloud_manager.remove("/cloud/borda.db", permanently=True)
    ycloud_manager.upload("db/borda.db", "/cloud/borda.db")

    upload_dir('static/images/uploads', 'cloud/images')


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


def main():
    db_session.global_init("db/borda.db")
    # for self
    # app.run(port=8080, host='127.0.0.1')
    # for internet

    # надеюсь, что когда хироку уходит в ребут,
    # то он начинает работать отсюда
    download_bd(enable_download_image=enable_image_sync_with_cloud)
    check_bd()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
