import sqlite3


# Добавление столбцов
# db_vote = sqlite3.connect("tguser.db")
# cur_vote = db_vote.cursor()
# cur_vote.execute("""ALTER TABLE polls ADD COLUMN region TEXT""")
# db_vote.commit()

class DB_poll(object):
    db_vote = sqlite3.connect("tguser.db")
    cur_vote = db_vote.cursor()
    cur_vote.execute("""CREATE TABLE IF NOT EXISTS polls (
        user_id INT PRIMARY KEY,
        poll_id INTEGER,
        photos BLOB,
        region TEXT);
        """)
    db_vote.commit()

    def return_user_id(self):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute("SELECT user_id FROM polls")
        user_id_all = cur_vote.fetchall()
        db_vote.close()
        user_id_all_list = []
        for i in user_id_all:
            user_id_all_list.append(i[0])
        print(user_id_all_list)
        return user_id_all_list



    def return_poll_id(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT poll_id FROM polls WHERE user_id = {'user_id'};")
        poll_id_own = cur_vote.fetchone()
        db_vote.close()
        poll_id_own_list = poll_id_own[0]
        print(poll_id_own_list)
        return poll_id_own_list



    def return_photos(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT photos FROM polls WHERE user_id = {'user_id'};")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        print(photos_own_list)
        return photos_own_list



