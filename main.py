import os
import sqlite3
import records


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


DB_ROOT_PATH = "./"


def user_balance_list(c, type="max"):
    order_by = "desc"
    if type == "min":
        order_by = ""

    sql_str = "select * from actors where id not in ('t01','t00','t04','t03') and cast(balance as float) > 0   group by id order by cast(balance as float) {} ,id limit 0,20 ".format(order_by)
    cursor = c.execute(sql_str)
    if type == "min":
        return [{"id": row['id'], "transformed_data":float(row["balance"]) * 10 ** -17, "base_num": "{:.17f}".format(float(row["balance"]))}for row in cursor]

    return [{"id": row['id'], "transformed_data":float(row["balance"]) * 10 ** -17, "base_num":row["balance"]}for row in cursor]


if __name__ == "__main__":
    current_path = os.path.join(DB_ROOT_PATH)
    os.chdir(current_path)
    conn = sqlite3.connect("chainwatch.db")
    conn.row_factory = dict_factory
    c = conn.cursor()
    # 剔除了 t01
    cursor = c.execute("select balance from actors where id not in ('t01','t00','t04','t03') ")
    num = 0.0
    base_num = 0.0
    for row in cursor:
        num += float(row["balance"])
    user_balance_list(c)

    max_big_to_small = user_balance_list(c)
    sorted_list = user_balance_list(c, "min")

    sorted_list = sorted(sorted_list, key=lambda items: items["base_num"], reverse=True)

    xlsx_list = max_big_to_small + [{}]+sorted_list +[{"id": "", "transformed_data": "{:.2f}".format(float(num) * 10 ** -17), "base_num": "{:.2f}".format(num)}]
    result = records.RecordCollection(iter(xlsx_list))
    with open("./demo.xlsx", "wb") as f:
        f.write(result.export("xlsx"))
