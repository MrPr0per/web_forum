from data.posts import Post
from data import db_session

db_session.global_init("db/borda.db")
db_sess = db_session.create_session()


def walk(tree, deep=0):
    if len(tree.keys()) == 0:
        return
    for k, v in tree.items():
        print('\t' * deep, k, ': {', sep='')
        walk(v, deep=deep + 1)
        print('\t' * deep, '}')
    return


def walk_and_push(tree, reply_to, id):
    if len(tree.keys()) == 0:
        return
    for k, v in tree.items():
        if k == reply_to:
            tree[k][id] = {}
            return
        walk_and_push(v, reply_to, id)
    return


def walk_and_show(tree, deep=0):
    if len(tree.keys()) == 0:
        return
    for k, v in tree.items():
        print('\t' * deep, posts[k].title, posts[k].content)
        # print('\t' * deep, 'ответы:')
        walk_and_show(v, deep=deep + 1)
        # print('\t' * deep, '}')
    return


# tree = {
#     0: {
#         1: {
#             2: {
#                 4: {
#                 }
#             },
#             3: {
#             }
#         },
#         5: {
#         }
#     }
# }

tree = {0: {}}
posts = {0: Post()}

for post in db_sess.query(Post).all():
    walk_and_push(tree, post.reply_to_id, post.id)
    posts[post.id] = post
# print(tree)


walk_and_show(tree)
