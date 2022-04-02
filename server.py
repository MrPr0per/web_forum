from flask import Flask, render_template, request
from data import db_session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import redirect
from posting import create_post
app = Flask(__name__)
app.config['SECRET_KEY'] = 'in_fact_we_are_not_powerless_but_weak-willed__will_will_make_any_choice_right'

boards = [["разное","/abu","/b","/media","/r","soc"],
          ["тематика","/au","/bi","/biz","/bo","/cc"],
          ["творчество","/de","/di","/diy","/mus","/p","/pa"],
          ["политикка","/hry","/news","/po"]]


class Answer_Form(FlaskForm):
    title = StringField('введите заголовок', validators=[DataRequired()])
    messenge = StringField('введите ваше сообщение', validators=[DataRequired()])
    submit = SubmitField('Войти')

class Answer_button(FlaskForm):
    submit = SubmitField('ответить')

@app.route("/")
def index():
    return render_template("home.html", boards = boards)

@app.route("/messenge_to/<section>/<int:id>",methods=['GET', 'POST'])
def create_messenge(section,id):
    form = Answer_Form()
    if form.validate_on_submit():
        print(form.messenge._value())
        messenge = form.messenge._value()
        title = form.title._value()
        create_post(section,title,messenge,id)
        return redirect(f'/{section}')
    return render_template("messenge_form.html", form=form, to_id = id)

@app.route("/<db_section>" ,methods=['GET', 'POST'])
def index2(db_section):
    from draw_post_tree import get_format_posts, delete_data
    delete_data()
    format_posts = get_format_posts(db_section)
    form = Answer_button()
    # if form.validate_on_submit():
        # этот ретерн можно не писать
        # return redirect(f'/messenge_to/{db_section}/{id}')
    return render_template("main.html", format_posts=format_posts,form=form,section=db_section)

def main():
    db_session.global_init("db/borda.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
