from flask import Flask, render_template, request
from data import db_session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import redirect
from posting import create_post, create_folders
from draw_post_tree import get_format_posts, delete_data
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'in_fact_we_are_not_powerless_but_weak-willed__will_will_make_any_choice_right'

app.config['RECAPTCHA_PRIVATE_KEY']='6Leg6HMfAAAAAF0MjyD9vd1H392fpAqJzshcTaBE'
app.config['RECAPTCHA_PUBLIC_KEY']='6Leg6HMfAAAAACYotHYSQXjPQdhRCdHDoIfsd_br'

boards = [["разное", "/abu", "/b", "/media", "/r", "/soc"],
          ["тематика", "/au", "/bi", "/biz", "/bo", "/cc"],
          ["творчество", "/de", "/di", "/diy", "/mus", "/p", "/pa"],
          ["политикка", "/hry", "/news", "/po"]]

hidden_posts = dict()
buttons = dict()

filepath = "static/images/uploads/"


class Answer_Form(FlaskForm):
    # title = StringField('введите заголовок', validators=[DataRequired()])
    # messenge = StringField('введите ваше сообщение', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('запостить')


class Answer_button(FlaskForm):

    submit = SubmitField('ответить')


class Close_button(FlaskForm):
    submit2 = SubmitField('скрыть/открыть ответы')


@app.route("/")
def index():
    # create_folders(boards,filepath)
    return render_template("home.html", boards=boards)


@app.route("/messenge_to/<section>/<int:reply_to_id>", methods=['GET', 'POST'])
def create_messenge(section, reply_to_id):
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
            print("aboba")
        # title = form.title._value()

        create_post(section, title, messenge, reply_to_id, hidden_posts, filename)

        # format_posts=get_format_posts(section,buttons)
        # hide_posts(id,id,format_posts)
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
    global buttons

    # if not len(hidden_posts):
    if db_section == 'None':
        # print("flask is stupid shit for dumbasses")
        return ""

    delete_data()
    format_posts = get_format_posts(db_section, buttons)
    form2 = Close_button()
    if form2.validate_on_submit():
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
    return render_template("main.html", format_posts=format_posts, section=db_section, form2=form2,
                           hidden_posts=hidden_posts)

    # print(type(format_posts[index][1]))
    # этот ретерн можно не писать
    # return redirect(f'/messenge_to/{db_section}/{id}')
    # print(format_posts)


def main():
    db_session.global_init("db/borda.db")
    # for self
    #app.run(port=8080, host='127.0.0.1')
    # for internet
    #
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()

