from data import posts
from data import db_session

db_session.global_init("db/borda.db")
db_sess = db_session.create_session()
db_section = 'r'
a = getattr(posts, db_section)
print(len(list(db_sess.query(a).all())))

