from flask import Flask, render_template
from data import db_session
from data.posts import Post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'in_fact_we_are_not_powerless_but_weak-willed._will_will_make_any_choice_right'


@app.route("/")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post)
    return render_template("main.html", posts=posts)


def main():
    db_session.global_init("db/borda.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
