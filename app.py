import sqlite3
import numpy as np
from flask import Flask, render_template, request, escape
from sklearn import preprocessing


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
    recommended_recipes = recommended_recipe_list()
    return render_template('results.html', recommended_recipes=recommended_recipes)

def mood_sql():
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
    return recipe_list


def recommended_recipe_list():
    # データベースからデータを取得
    recipe_list = mood_sql()

    # POSTメソッドから取得した気分の値とレシピデータの気分の値のユークリッド距離を算出
    euclidean_distance_list = euclidean_distance(recipe_list)

    # ユークリッド距離の値のリストとレシピデータのリストを結合
    recommended_recipes = sort_by_euclidean_distance(recipe_list, euclidean_distance_list)

    return recommended_recipes


def euclidean_distance(recipe_list):

    # レシピデータの気分と分類を取得
    recipe_list_syusyoku = []
    recipe_list_syusai = []
    recipe_list_hukusai = []
    recipe_list_mood = []
    recipe_list_body = []
    recipe_list_money = []
    recipe_list_time = []

    # レシピデータの気分と分類をリストに格納(先頭行のラベルを除く)
    for row in recipe_list[1:]:
        recipe_list_syusyoku.append(int(list(row)[1]))  # 「主食」の行のみを抽出
        recipe_list_syusai.append(int(list(row)[2]))    # 「主菜」の行のみを抽出
        recipe_list_hukusai.append(int(list(row)[3]))   # 「副菜」の行のみを抽出
        recipe_list_mood.append(int(list(row)[4]))      # 「精神」の行のみを抽出
        recipe_list_body.append(int(list(row)[5]))      # 「身体」の行のみを抽出
        recipe_list_money.append(int(list(row)[6]))     # 「経済」の行のみを抽出
        recipe_list_time.append(int(list(row)[7]))      # 「時間」の行のみを抽出

    # POSTメソッドから取得したmoodの値(-5~5)をリストに保存
    squared_diff = []
    moods = recipe_list[0][4:8] # レシピデータの気分のラベルを取得['mood', 'body', 'money', 'time']

    # レシピデータの気分の値を標準化
    recipe_list_mood_std = preprocessing.scale(recipe_list_mood)
    recipe_list_body_std = preprocessing.scale(recipe_list_body)
    recipe_list_money_std = preprocessing.scale(recipe_list_money)
    recipe_list_time_std = preprocessing.scale(recipe_list_time)

    squared_diff_moods = [recipe_list_mood_std, recipe_list_body_std, recipe_list_money_std, recipe_list_time_std]

    # レシピデータの気分のラベルの数だけ繰り返す0~3
    for row in range(len(moods)):

        recipe_list_item = squared_diff_moods[row]

        # POSTメソッドから取得したmoodの値をリストに保存
        mood_value = [float(request.form[moods[row]])] * len(recipe_list_item)

        if float(request.form[moods[row]]) != 0:
            recipe_mood_array = np.array(recipe_list_item)
            mood_array = np.array(mood_value)
            diff_mood = recipe_mood_array - mood_array  # レシピデータの気分とPOSTメソッドから取得したmoodの値の差を計算
            squared_diff_mood = np.square(diff_mood)    # 差の2乗を計算
        else:   # スライダーが0を選択しているときはユークリッド距離を計算しない
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
    recipe_list_deleted_label = recipe_list[1:] # 先頭行のラベルを除く
    for row_num in range(len(recipe_list_deleted_label)):
        recipe_list_deleted_label[row_num].append(euclidean_distance_list[row_num])
        combined_list.append(recipe_list_deleted_label[row_num])

    # ユークリッド距離に基づいてリストをソート
    sorted_list = sorted(combined_list, key=lambda x: x[8])

    # 多様性検索の機能
    sorted_list_reciprocal = sort_list_reciprocal(sorted_list)
    recommended_recipe_list = greedy_reranking(sorted_list_reciprocal, 10, 0.5)

    return recommended_recipe_list


# リストの要素の値を逆数にしてリストを返す
# 検索結果を降順にソートするために使用
def sort_list_reciprocal(sorted_list):
    sorted_list_reciprocal = []

    for i in range(len(sorted_list)):
        sorted_item_reciprocal = sorted_list[i][0:8]
        sorted_list_reciprocal.append(sorted_item_reciprocal)
        sorted_list_reciprocal[i].append(1/sorted_list[i][8])

    return sorted_list_reciprocal


# コサイン類似度を計算したリストを返す
def similarity(i, R):

    v1 = i[1:4]
    sim_list = []
    eps = 1e-8

    for j in R:
        v2 = j[1:4]
        sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)) + eps
        sim_list.append(sim)
    return sim_list


# 検索結果のリストを多様性を考慮してリランキング
def select_item_id(sorted_list, R, alpha):
    C = sorted_list
    max_score = -1
    max_score_item_id = -1
    for i in C:
        if len(R) == 0:
            return i

        score = alpha * i[8] - (1 - alpha) * max(similarity(i, R))

        if score > max_score:
            max_score = score
            max_score_item_id = i
    return max_score_item_id


# 多様性を考慮したリランキングを行う
def greedy_reranking(C, N, alpha):
    results = []
    while len(results) < N:
        doc_id = select_item_id(C, results, alpha)
        results.append(doc_id)
        C.remove(doc_id)
        
    return results


if __name__ == "__main__":
    app.run(debug=True)