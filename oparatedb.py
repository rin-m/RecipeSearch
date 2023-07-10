import sqlite3

# カレントディレクトリにdbがなければ、作成
# すでにdbが作成されていれば、dbに接続
dbname = 'recipe.db'
conn = sqlite3.connect(dbname)

# sqliteを操作するカーソルオブジェクトを作成
cur = conn.cursor()

# データベースを削除
#cur.execute("drop table recipe;")

# テーブルのCreate文を実行
#cur.execute("create table recipe(title text, summary text, cook text, calorie int, ingredient text, explanation text);")

# サンプルの挿入
#cur.execute("insert into recipe values('肉じゃが', '肉じゃがのレシピです。', '筑波太郎', 100, '豚肉、じゃがいも', '煮込んで味を付ける');")
#cur.execute("insert into recipe values('カレー', 'カレーのレシピです。', '筑波二郎', 700, '豚肉、じゃがいも、カレールー', '煮込む');")

# テーブルの中身を表示
for a in cur.execute("select * from recipe;"):
	print(a)

# データベースの変更を確定する
conn.commit()

# データベースへのコネクションを閉じる
conn.close()