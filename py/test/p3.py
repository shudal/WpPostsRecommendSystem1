#coding:utf-8

# 这个是弄到自己新建的表里，已抛弃此版本
import os
import configparser
import pymysql

print("Reading config file...")

cur_path=os.path.dirname(os.path.realpath(__file__))
config_path=os.path.join(cur_path,'config.ini')
conf=configparser.ConfigParser()
conf.read(config_path)

#从配置文件中获取数据信息
db_host             = conf.get('database', 'host')
db_port             = int(conf.get('database', 'port'))
db_user             = conf.get('database', 'user')
db_password         = conf.get('database', 'password')
db_database_name    = conf.get('database','database')
db_table_prefix     = conf.get('database', 'table_prefix')
db_config = {'host' : db_host, 'port' : db_port, 'user' : db_user, 'password' : db_password, 'db' : db_database_name, 'prefix' : db_table_prefix}

print("Connecting database...")
#连接数据库
db = pymysql.connect(host = db_config['host'],port = db_config['port'], user = db_config['user'], password  = db_config['password'], db = db_config['db'], charset = 'utf8mb4')
cursor = db.cursor()

print("Reading the view history...")
sql_query_history = "select * from " + db_config['prefix']  + "_usermeta where meta_key='_perci_haku_viewed'"
cursor.execute(sql_query_history)
history = cursor.fetchall()

dict = []
for i in range(0, len(history)):
	postids = history[i][3][1:]
	postids = postids.split('|')
	
	# 去重
	postids = list(set(postids))
	
	for k in range(0, len(postids)):
		d = {'userid' : history[i][1], 'postid' : postids[k]}
		dict.append(d)

# print(dict)

# 匹配文章的作者id
print("Matching the author id...")
sql_query_posts = "select id, post_author from " + db_config['prefix'] + "_posts"
cursor.execute(sql_query_posts)
all_posts = cursor.fetchall()
for i in range(0, len(dict)):
	tai = 1
	for k in range(0, len(all_posts)):
		if (tai == 0):
			break;
		if (str(all_posts[k][0]) == dict[i]['postid']):
			dict[i]['author_id'] = all_posts[k][1]
			tai = 0;

# 匹配文章的分类id
print("Matching the category id...")
sql_query_cat = "select object_id, term_taxonomy_id from " + db_config['prefix'] + "_term_relationships"
cursor.execute(sql_query_cat)
all_cats = cursor.fetchall()
for i in range(0, len(dict)):
	tai = 1
	for k in range(0, len(all_cats)):
		if (tai == 0):
			break;
		if (str(all_cats[k][0]) == dict[i]['postid']):
			dict[i]["cat_id"] = all_cats[k][1]
			tai = 0;
import numpy as np
dict = np.array(dict)

from lightfm.data import Dataset

print("Build the dataset...")
dataset = Dataset()
dataset.fit((x['userid'] for x in dict), (x['postid'] for x in dict))
dataset.fit_partial(items=(x['postid'] for x in dict), item_features=(x['author_id'] for x in dict))
dataset.fit_partial(items=(x['postid'] for x in dict), item_features=(x["cat_id"] for x in dict))

num_users, num_items = dataset.interactions_shape()

(interactions, weights) = dataset.build_interactions(((x['userid'], x['postid']) for x in dict))

from lightfm import LightFM

print("Training the model...")
model = LightFM(loss='warp')
model.fit(interactions)
from lightfm.evaluation import precision_at_k

import numpy as np
print("Train precision: %.2f" % precision_at_k(model, interactions, k=5).mean())


posts 	= []
userids2 = []
for i in range(0, len(dict)):
	userids2.append(dict[i]['userid'])
	posts.append(dict[i]['postid'])

userids = list(set(userids2))
userids.sort(key=userids2.index)
posts = np.array(posts)
def recommend(model, data, userid):
	n_users, n_items = data.shape

	scores = model.predict(userid, np.arange(n_items))
	top_items = posts[np.argsort(-scores)]
	if (len(top_items) >= 10):
		top_items = top_items[:10]

	userid = userids[userid]
	save_recoitems(userid, top_items)

def save_recoitems(userid, top_items):
	sql_get_perreco = "select postid from perci_haku_reco where userid='" + str(userid) + "'"
	cursor.execute(sql_get_perreco)
	data = cursor.fetchone()
	
	if data is None:
		sql_set_perreco = "insert into perci_haku_reco (`userid`, `postid`) values ('" + str(userid) + "', '"	
	else :
		sql_set_perreco = "update perci_haku_reco set postid='"

	
	for i in range(0, len(top_items)):
		sql_set_perreco = sql_set_perreco + "|" + top_items[i]
	
	if data is None:
		sql_set_perreco = sql_set_perreco + "')"
	else:
		sql_set_perreco = sql_set_perreco  + "' where userid='" + str(userid) + "'"
	
	try :
		cursor.execute(sql_set_perreco)
		db.commit()
	except Exception as e:
		print(str(e))
		db.rollback()

for i in range(0, len(userids)):
	print("Recomending posts for userid=" + str(userids[i]) + "...")
	recommend(model, interactions, i)
# p = model.predict_rank(interactions)
# print(p)
db.close()

print("finished!")
