from data import db_session


db_session.global_init("db/borda.db")
db_sess = db_session.create_session()

tree = {0: {}}
posts2 = dict()
format_posts = []

def delete_data():
    global tree, posts2,format_posts
    tree = {0: {}}
    posts2 = dict()
    format_posts = []


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


def walk_and_show(tree, buttons,deep=0):

    global posts2
    if len(tree.keys()) == 0:
        return
    for k, v in tree.items():
        # print('\t' * deep, posts[k].title, posts[k].content)
        if k in buttons.keys():
            format_posts.append((deep, posts2[k],buttons[k]))
        else:
            if deep == 1:
                format_posts.append((deep, posts2[k],1))
            else:
                format_posts.append((deep, posts2[k],0))
        #                                           /.\
        # ___________________________________________|
        # этот костыль нужен для закрытия постов, которые не читаешь, да, я знаю, что гений проектирования
        # если значение == 0, то закрывающей кнопки нет
        # если значение == 1, то закрывающая кнопка есть, но она выключена
        # если значение == 2, то закрывающая кнопка есть, и она включена

        # print('\t' * deep, 'ответы:')
        walk_and_show(v, buttons, deep=deep + 1)
        # print('\t' * deep, '}')
    return

# def load(db_section):
#     result = None
#     exec('from data.posts import ' + db_section)
#     exec('result = ' + db_section)
#     return result

def get_format_posts(db_section,buttons):
    from data import posts

    a = getattr(posts,db_section)
    global posts2
    posts2 = {0: a()}
    if not format_posts:
        for post in db_sess.query(a).all():
            walk_and_push(tree, post.reply_to_id, post.id)
            posts2[post.id] = post
        # print(tree)
        walk_and_show(tree,buttons)

        # for i in format_posts:
        #     print(i)

    return format_posts
