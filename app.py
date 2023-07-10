import sqlite3
import numpy as np
from flask import Flask, render_template, request, escape


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

'''
# キーワード検索
@app.route("/sample1", methods = ["POST"])
def sample1():
    k = keyword_sql()
    con = sqlite3.connect("recipe.db")
    cur = con.cursor()
    s = "<!DOCTYPE html>\n"
    s += '<html><head><meta charset="UTF-8"><title>検索結果</title></head>\n<body>'
    s += '<div><h1>検索結果</h1></div>\n'
    for row in cur.execute("{}".format(k)):
        s += "<div><p>{}<hr></p></div>".format(escape(row[0]))
    con.close()
    s += "</body></html>"
    return s


#区切り文字で検索キーワードを分割してsql文を生成
def keyword_sql():
    l = request.form["keyword"]
    if l != "":
        m = l.split()
        n = "select * from recipe where "
        for o in m:
            n += "(name like '%{}%') and ".format(o,o)
        n = n.rstrip(' and ')
        n += ';'
    else:
        n = "select * from recipe;"
    return n
'''

@app.route("/mood1", methods = ["POST"])
def mood1():
    # テンプレートに結果を渡してレンダリング
    recommended_recipes = mood_list()
    return render_template('results.html', recommended_recipes=recommended_recipes)

def mood_list():
    # データベースに接続
    conn = sqlite3.connect("recipe.db")
    cursor = conn.cursor()

    # データベースからデータを取得
    cursor.execute('SELECT * FROM recipe')
    result = cursor.fetchall()

    # 取得したデータをリストに格納
    recipe_list = []
    for row in result:
        recipe_list.append(list(row))

    # データベース接続を閉じる
    cursor.close()
    conn.close()

    # POSTメソッドから取得した気分の値とレシピデータの気分の値のユークリッド距離を算出
    euclidean_distance_list = euclidean_distance(recipe_list)

    # ユークリッド距離の値のリストとレシピデータのリストを結合
    recommended_recipes = sort_by_euclidean_distance(recipe_list, euclidean_distance_list)

    return recommended_recipes


def euclidean_distance(recipe_list_items):

    # レシピデータの気分を取得
    recipe_list_mood = []
    recipe_list_body = []
    recipe_list_taste = []
    recipe_list_time = []
    recipe_list_money = []
    recipe_list_modify = []
    for row in recipe_list_items:
        recipe_list_mood.append(int(list(row)[1]))  # 「精神」の行のみを抽出
        recipe_list_body.append(int(list(row)[2]))  # 「身体」の行のみを抽出
        recipe_list_taste.append(int(list(row)[3]))  # 「味覚」の行のみを抽出
        recipe_list_time.append(int(list(row)[4]))  # 「時間」の行のみを抽出
        recipe_list_money.append(int(list(row)[5]))  # 「経済」の行のみを抽出
        recipe_list_modify.append(int(list(row)[6]))  # 「変化」の行のみを抽出

    # POSTメソッドから取得したmoodの値(-5~5)をリストに保存
    squared_diff = []
    moods = ["mood", "body", "taste", "time", "money", "modify"]
    squared_diff_moods = [recipe_list_mood, recipe_list_body, recipe_list_taste, recipe_list_time, recipe_list_money, recipe_list_modify]

    for row in range(len(moods)):

        # 「(例)精神」の行のみのリスト
        recipe_list_item = squared_diff_moods[row]

        mood_value = [float(request.form[moods[row]])] * len(recipe_list_item)

        if float(request.form[moods[row]]) != 0:
            recipe_mood_array = np.array(recipe_list_item)
            mood_array = np.array(mood_value)
            diff_mood = recipe_mood_array - mood_array
            squared_diff_mood = np.square(diff_mood)
        else: # スライダーが0を選択しているときはユークリッド距離を計算しない
            squared_diff_mood = np.zeros(len(recipe_list_item), int)

        squared_diff.append(squared_diff_mood)
    
    # 各列の合計を求める
    squared_diff_columns_sum = map(sum, zip(*squared_diff))

    # 各要素の平方根を求める
    euclidean_distance_list = np.sqrt(list(squared_diff_columns_sum))

    return euclidean_distance_list


def sort_by_euclidean_distance(recipe_list, euclidean_distance_list):
    # ユークリッド距離の値のリストとデータベースから取得したデータのリストを結合
    combined_list = []
    for row_num in range(len(recipe_list)):
        recipe_list[row_num].append(euclidean_distance_list[row_num])
        combined_list.append(recipe_list[row_num])
    
    # ユークリッド距離に基づいてリストをソート
    sorted_list = sorted(combined_list, key=lambda x: x[7])

    return sorted_list


if __name__ == "__main__":
    app.run(debug=True)