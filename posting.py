from data.posts import b,abu #это надо будет стереть
from data import db_session

db_session.global_init("db/borda.db")
db_sess = db_session.create_session()

def create_post(section, title,messenge,reply_to_id,file=""):
    from data import posts
    a = getattr(posts, section)
    post = a(title=title, content=messenge, reply_to_id=reply_to_id)
    db_sess.add(post)
    db_sess.commit()
    pass

for post in db_sess.query(b).all():
    db_sess.delete(post)
for post in db_sess.query(abu).all():
    db_sess.delete(post)
db_sess.commit()

posts = [
    b(title="Первый пост", content="сап трич", reply_to_id=0),
    b(title="второй пост", content="привет привет", reply_to_id=1),
    b(title="бебра", content="сап", reply_to_id=1),
    b(title="ответ второго уровня", content="ответ второго уровня", reply_to_id=2, files="static/images/yoba.png"),
    b(title="ТРИЧ, сейчас я расскажу, как я устроился на работу", content="*история про говно*", reply_to_id=0),
    b(title="тред головы", content="голова, дай деняк", reply_to_id=5, files="static/images/yoba.png"),
    b(title="сейчас я вам расскажу историю, как я наполнял пакеты водой и кидал с 9 этажа", content="", reply_to_id=0, files="static/images/yoba.png"),
    abu(title="3ch успешно создается", content="скро появятся истории про говно",reply_to_id=0, files="static/images/yoba.png")
]
for post in posts:
    db_sess.add(post)
db_sess.commit()