from data.posts import b, abu, User  # это надо будет стереть
from data import db_session
import os

db_session.global_init("db/borda.db")
db_sess = db_session.create_session()


def create_post(section, title, messenge, reply_to_id, hidden_posts, time, file=None):
    from data import posts
    a = getattr(posts, section)
    if file:
        post = a(title=title, content=messenge, reply_to_id=reply_to_id, created_date=time, files=file)
    else:
        post = a(title=title, content=messenge, reply_to_id=reply_to_id, created_date=time)

    db_sess.add(post)
    db_sess.commit()
    if reply_to_id in hidden_posts.keys():
        hidden_posts[reply_to_id].append(post.id)


def create_folders(boards, filepath):
    for i in boards:
        for j in range(1, len(i)):
            if not os.path.exists(i[j]):
                os.mkdir(filepath + i[j])


# for post in db_sess.query(b).all():
#     db_sess.delete(post)
# for post in db_sess.query(abu).all():
#     db_sess.delete(post)
# for post in db_sess.query(User).all():
#     db_sess.delete(post)
# db_sess.commit()
# user = User()
# user.nickname = "goldenman"
# user.set_password("super-puper_password228")
# user.verifyed = True
# db_sess.add(user)
# db_sess.commit()

# posts = [
#     b(title="Первый пост", content="сап трич", reply_to_id=0),
#     b(title="второй пост", content="привет привет", reply_to_id=1),
#     b(title="бебра", content="сап", reply_to_id=1),
#     b(title="ответ второго уровня", content="ответ второго уровня", reply_to_id=2, files="static/images/yoba.png"),
#     b(title="ТРИЧ, сейчас я расскажу, как я устроился на работу", content="*история про говно*", reply_to_id=0),
#     b(title="тред головы", content="голова, дай деняк", reply_to_id=5, files="static/images/yoba.png"),
#     b(title="сейчас я вам расскажу историю, как я наполнял пакеты водой и кидал с 9 этажа", content="", reply_to_id=0, files="static/images/yoba.png"),
#     abu(title="3ch успешно создается", content="скро появятся истории про говно",reply_to_id=0, files="static/images/yoba.png")
# ]
# for post in posts:
#     db_sess.add(post)
# db_sess.commit()
