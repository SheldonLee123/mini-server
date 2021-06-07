# -*- coding: utf-8 -*-
# @Time    : 2021/5/22 10:09 PM
# @Author  : Sheldon
# @FileName: MyFlask.py
# @Software: PyCharm
# @Description: description
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

base_url = "http://127.0.0.1:5000"
# base_url = "http://172.16.7.18:5000"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Rotogram(db.Model):  # 表名将会是 rotogram（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    image_src = db.Column(db.String(120))  # url website
    open_type = db.Column(db.String(20), default="navigate")
    goods_id = db.Column(db.Integer)
    navigator_url = db.Column(db.String(120))

    def format(self):
        return dict(id=self.id, image_src=base_url + self.image_src, open_type=self.open_type, goods_id=self.goods_id, navigator_url=self.navigator_url)

    # def __init__(self, image_src, open_type, goods_id, navigator_url):
    #     self.image_src = image_src
    #     self.open_type = open_type
    #     self.goods_id = goods_id
    #     self.navigator_url = navigator_url

    def __repr__(self):
        return 'Rotogram %s' % self.id

class Goods(db.Model):
    goods_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_id1 = db.Column(db.Integer, db.ForeignKey('categories1.cat_id1'))
    cat_id2 = db.Column(db.Integer, db.ForeignKey('categories2.cat_id2'))
    goods_name = db.Column(db.String(120))
    goods_price = db.Column(db.Integer)
    goods_number = db.Column(db.Integer)
    goods_weight = db.Column(db.Integer)
    goods_big_logo = db.Column(db.String(120))
    goods_small_logo = db.Column(db.String(220))
    add_time = db.Column(db.DateTime, default=datetime.now)
    upd_time = db.Column(db.DateTime, default=datetime.now,onupdate=datetime.now)

    def format(self):
        return dict(goods_id=self.goods_id, goods_name=self.goods_name, goods_price=self.goods_price, goods_big_logo=self.goods_big_logo, goods_small_logo=self.goods_small_logo, add_time=self.add_time)

    def __repr__(self):
        return 'Goods %s' % self.goods_name

class Categories1(db.Model):
    cat_id1 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(20))
    img_src = db.Column(db.String(120))
    goods = db.relationship("Goods", backref="categories1")
    children = db.relationship("Categories2", backref="child_cat")

    def format(self):
        return dict(cat_id1=self.cat_id1, cat_name=self.cat_name, img_src=base_url + self.img_src)

    def __repr__(self):
        return 'Categories1 %s' % self.cat_name

class Categories2(db.Model):
    cat_id2 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories1.cat_id1'))
    cat_name = db.Column(db.String(20))
    cat_icon = db.Column(db.String(120), default="https://gw.alicdn.com/tfs/TB1CoEwVrvpK1RjSZFqXXcXUVXa-185-144.png")
    goods = db.relationship("Goods", backref="categories2")

    def format(self):
        return dict(cat_id2=self.cat_id2, cat_name=self.cat_name, cat_icon=base_url + self.cat_icon)

    def __repr__(self):
        return 'Categories2 %s' % self.cat_name

@app.route('/get_rotogram')
def rotogram():
    return_dict = {'meta': {"msg": 200, "status": "Success"}, 'message': None}
    Rotograms = []
    for i in Rotogram.query.all():
        Rotograms.append(i.format())
    # print(type(Rotograms))
    # print(Rotograms)
    return_dict['message'] = Rotograms
    return jsonify(return_dict)

@app.route('/catlists')
def catlists():
    return_dict = {'meta': {"msg": 200, "status": "Success"}, 'message': None}
    catlists = []
    for i in Categories1.query.all():
        catlists.append(i.format())
    return_dict['message'] = catlists
    return jsonify(return_dict)

@app.route('/goods')
def goods():
    return_dict = {'meta': {"msg": 200, "status": "Success"}, 'message': None}
    pagenum = request.args.get("pagenum")
    pagesize = request.args.get("pagesize")
    if pagenum == None:
        pagenum = 1
    else:
        pagenum = int(pagenum)
    if pagesize == None:
        pagesize = 10
    else:
        pagesize = int(pagesize)
    total = Goods.query.count()
    goods_list = []
    start_item = total // pagesize * pagenum
    # print(start_item)
    # print(start_item+pagesize-1)
    for i in Goods.query.all()[start_item: start_item+pagesize-1]:
        goods_list.append(i.format())
    message = {'total': total, 'pagenum': pagenum, 'goods': goods_list}
    return_dict['message'] = message
    return jsonify(return_dict)

@app.route('/categories')
def categories():
    return_dict = {'meta': {"msg": 200, "status": "Success"}, 'message': None}
    categories_list = []
    for i in Categories1.query.all():
        categories_dict = i.format()
        children_list = []
        categories2 = Categories2.query.filter_by(parent_id=i.cat_id1).all()
        for j in categories2:
            children_list.append(j.format())
        categories_dict['children'] = children_list
        categories_list.append(categories_dict)
    return_dict['message'] = categories_list
    return jsonify(return_dict)

@app.route('/get_pubcatelist')
def pubcatelist():
    return_dict = {'meta': {"msg": 200, "status": "Success"}, 'message': None}
    cate_id = request.args.get("cate_id")
    catelist = []
    if cate_id == "1" or cate_id == "2" or cate_id == "3":
        for i in Categories2.query.filter_by(parent_id=cate_id).all():
            catelist.append(i.format())
    elif cate_id == "4":
        for i in Categories2.query.filter(Categories2.parent_id>4).all():
            catelist.append(i.format())
    return_dict['message'] = catelist
    return jsonify(return_dict)

if __name__ == '__main__':
    # 删除表
    db.drop_all()
    # 创建表
    db.create_all()

    Rotogram1 = Rotogram(image_src='/static/imgs/index1.jpeg')
    Rotogram2 = Rotogram(image_src='/static/imgs/index2.jpeg')
    Rotogram3 = Rotogram(image_src='/static/imgs/index3.jpeg')
    # Rotogram4 = Rotogram(image_src='https://img.alicdn.com/imgextra/i3/2206686532409/O1CN01yJc6Lt1TfMncjGrwa_!!2206686532409-0-lubanimage.jpg')
    db.session.add(Rotogram1)
    db.session.add(Rotogram2)
    db.session.add(Rotogram3)
    # db.session.add(Rotogram4)

    goods1 = Goods(goods_name="京华18L大容量 双核制冷超静音车载冰箱车家两用宿舍迷你冰箱家用小型冰箱微小冷藏箱胰岛素箱", goods_price=468, goods_big_logo="http://image3.suning.cn/uimg/b2c/newcatentries/0070084763-000000000157625708_1_800x800.jpg", goods_small_logo="http://image3.suning.cn/uimg/b2c/newcatentries/0070084763-000000000157625708_1_400x400.jpg")
    goods2 = Goods(goods_name="婷微（Tingwei）车载冰箱 CB-08B 升级版 空气净化款半导体电子制冷冷暖冰箱388mm*200mm*278mm", goods_price=258, goods_big_logo="http://image4.suning.cn/uimg/b2c/newcatentries/0000000000-000000000600622540_1_800x800.jpg",goods_small_logo="http://image4.suning.cn/uimg/b2c/newcatentries/0000000000-000000000600622540_1_400x400.jpg")
    db.session.add(goods1)
    db.session.add(goods2)

    categories1 = Categories1(cat_name="出二手", img_src="/static/imgs/used.jpg")
    categories2 = Categories1(cat_name="收二手", img_src="/static/imgs/collect_used.jpg")
    categories3 = Categories1(cat_name="转租收租", img_src="/static/imgs/to_let.jpg")
    categories4 = Categories1(cat_name="兼职信息", img_src="/static/imgs/part-time_job.jpg")
    categories5 = Categories1(cat_name="本地优惠", img_src="/static/imgs/local_offers.jpg")
    categories6 = Categories1(cat_name="包车接机", img_src="/static/imgs/charter_bus.jpg")
    categories7 = Categories1(cat_name="组局派对", img_src="/static/imgs/group_parties.jpg")
    categories8 = Categories1(cat_name="全部分类", img_src="/static/imgs/all_categories.jpg")
    db.session.add(categories1)
    db.session.add(categories2)
    db.session.add(categories3)
    db.session.add(categories4)
    db.session.add(categories5)
    db.session.add(categories6)
    db.session.add(categories7)
    db.session.add(categories8)

    categories1 = Categories2(cat_name="推荐物品", parent_id="1", cat_icon="/static/imgs/Recommended.jpg")
    categories2 = Categories2(cat_name="厨房用品", parent_id="1", cat_icon="/static/imgs/Kitchen.jpg")
    categories3 = Categories2(cat_name="家具家电", parent_id="1", cat_icon="/static/imgs/Furniture.jpg")
    categories4 = Categories2(cat_name="书籍文具", parent_id="1", cat_icon="/static/imgs/Books.jpg")
    categories6 = Categories2(cat_name="电子产品", parent_id="1", cat_icon="/static/imgs/Electronic.jpg")
    categories5 = Categories2(cat_name="服饰鞋包", parent_id="1", cat_icon="/static/imgs/Clothing.jpg")
    categories7 = Categories2(cat_name="美妆护肤", parent_id="1", cat_icon="/static/imgs/Beauty.jpg")
    categories8 = Categories2(cat_name="药品", parent_id="1", cat_icon="/static/imgs/Medicines.jpg")
    categories9 = Categories2(cat_name="运动", parent_id="1", cat_icon="/static/imgs/Sports.jpg")
    categories10 = Categories2(cat_name="食材", parent_id="1", cat_icon="/static/imgs/Food.jpg")
    categories11 = Categories2(cat_name="推荐物品", parent_id="2", cat_icon="/static/imgs/Recommended.jpg")
    categories12 = Categories2(cat_name="厨房用品", parent_id="2", cat_icon="/static/imgs/Kitchen.jpg")
    categories13 = Categories2(cat_name="家具家电", parent_id="2", cat_icon="/static/imgs/Furniture.jpg")
    categories14 = Categories2(cat_name="书籍文具", parent_id="2", cat_icon="/static/imgs/Books.jpg")
    categories15 = Categories2(cat_name="服饰鞋包", parent_id="2", cat_icon="/static/imgs/Clothing.jpg")
    categories16 = Categories2(cat_name="电子产品", parent_id="2", cat_icon="/static/imgs/Electronic.jpg")
    categories17 = Categories2(cat_name="美妆护肤", parent_id="2", cat_icon="/static/imgs/Beauty.jpg")
    categories18 = Categories2(cat_name="药品", parent_id="2", cat_icon="/static/imgs/Medicines.jpg")
    categories19 = Categories2(cat_name="运动", parent_id="2", cat_icon="/static/imgs/Sports.jpg")
    categories20 = Categories2(cat_name="食材", parent_id="2", cat_icon="/static/imgs/Food.jpg")
    categories21 = Categories2(cat_name="ensuit", parent_id="3", cat_icon="/static/imgs/ensuite.jpg")
    categories22 = Categories2(cat_name="studio", parent_id="3", cat_icon="/static/imgs/studio.jpg")
    categories23 = Categories2(cat_name="one-bedroom", parent_id="3", cat_icon="/static/imgs/one-bedroom.jpg")
    categories24 = Categories2(cat_name="apartment", parent_id="3", cat_icon="/static/imgs/apartment.jpg")
    categories24 = Categories2(cat_name="flat", parent_id="3", cat_icon="/static/imgs/flat.jpg")
    categories25 = Categories2(cat_name="兼职信息", parent_id="4", cat_icon="/static/imgs/Recommended.jpg")
    categories26 = Categories2(cat_name="本地优惠", parent_id="5", cat_icon="/static/imgs/Recommended.jpg")
    categories27 = Categories2(cat_name="包车接机", parent_id="6", cat_icon="/static/imgs/Recommended.jpg")
    categories28 = Categories2(cat_name="狼人杀", parent_id="7", cat_icon="/static/imgs/Langrensha.jpg")
    categories29 = Categories2(cat_name="剧本杀", parent_id="7", cat_icon="/static/imgs/Jubensha.jpg")
    categories30 = Categories2(cat_name="运动健身", parent_id="7", cat_icon="/static/imgs/Sports.jpg")
    categories31 = Categories2(cat_name="洋酒鉴赏", parent_id="7", cat_icon="/static/imgs/Drink.jpg")
    categories32 = Categories2(cat_name="网球", parent_id="7", cat_icon="/static/imgs/Sports.jpg")
    categories33 = Categories2(cat_name="麻将德州", parent_id="7", cat_icon="/static/imgs/Majiang.jpg")
    db.session.add(categories1)
    db.session.add(categories2)
    db.session.add(categories3)
    db.session.add(categories4)
    db.session.add(categories5)
    db.session.add(categories6)
    db.session.add(categories7)
    db.session.add(categories8)
    db.session.add(categories9)
    db.session.add(categories10)
    db.session.add(categories11)
    db.session.add(categories12)
    db.session.add(categories13)
    db.session.add(categories14)
    db.session.add(categories15)
    db.session.add(categories16)
    db.session.add(categories17)
    db.session.add(categories18)
    db.session.add(categories19)
    db.session.add(categories20)
    db.session.add(categories21)
    db.session.add(categories22)
    db.session.add(categories23)
    db.session.add(categories24)
    db.session.add(categories25)
    db.session.add(categories26)
    db.session.add(categories27)
    db.session.add(categories28)
    db.session.add(categories29)
    db.session.add(categories30)
    db.session.add(categories31)
    db.session.add(categories32)
    db.session.add(categories33)

    db.session.commit()

    app.run(debug=True, host='0.0.0.0', port=5000)