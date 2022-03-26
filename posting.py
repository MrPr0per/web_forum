from data.posts import Post
from data import db_session

db_session.global_init("db/borda.db")
db_sess = db_session.create_session()

for post in db_sess.query(Post).all():
    db_sess.delete(post)
db_sess.commit()

posts = [
    Post(title="Первый пост", content="сап трич", reply_to_id=0),
    Post(title="второй пост", content="привет привет", reply_to_id=1),
    Post(title="бебра", content="сап", reply_to_id=1),
    Post(title="ответ второго уровня", content="ответ второго уровня", reply_to_id=2),
    Post(title="ТРИЧ, сейчас я расскажу, как я устроился на работу", content="*история про говно*", reply_to_id=0),
    Post(title="", content="блять", reply_to_id=5),
]
for post in posts:
    db_sess.add(post)
db_sess.commit()
