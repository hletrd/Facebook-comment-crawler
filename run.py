import requests
import config
import sqlite3
import sys

size = 200

r = requests.get('https://graph.facebook.com/v2.7/' + config.userid + '_' + config.postid + '/comments?access_token=' + config.access_token + '&__mref=message_bubble&limit=' + str(size) + '&fields=message,id,from,created_time,attachment')
data = r.json()
url = data['paging']['next']
dbc = sqlite3.connect(config.db)
dbc.text_factory = str
c = dbc.cursor()
try:
	sys.stderr.write('Creating table\n')
	c.execute("CREATE TABLE comments(date TEXT, name TEXT, userid TEXT, message TEXT, id TEXT, type TEXT, media_image_src TEXT, media_image_width TEXT, media_image_height TEXT, target_id TEXT, target_url TEXT, url TEXT, title TEXT, description TEXT);")
except:
	sys.stderr.write('Table exists\n')
dbc.commit()

cnt = 0
while True:
	cnt+=1
	r = requests.get(url)
	data = r.json()
	date_tmp = ''
	for i in data['data']:
		try:
			if 'attachment' in i:
				if not 'target' in i['attachment']:
					i['attachment']['target'] = {}
				if not 'id' in i['attachment']['target']:
					i['attachment']['target']['id'] = ''
				if not 'url' in i['attachment']['target']:
					i['attachment']['target']['url'] = ''
				if not 'description' in i['attachment']:
					i['attachment']['description'] = ''
				if not 'title' in i['attachment']:
					i['attachment']['title'] = ''
				if i['attachment']['type'] == 'share':
					if 'media' in i['attachment']:
						c.execute("INSERT INTO comments (date, name, userid, message, id, type, media_image_src, media_image_width, media_image_height, target_id, target_url, url, title, description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);", (i['created_time'], i['from']['name'], i['from']['id'], i['message'], i['id'], i['attachment']['type'], i['attachment']['media']['image']['src'], i['attachment']['media']['image']['width'], i['attachment']['media']['image']['height'], i['attachment']['target']['id'], i['attachment']['target']['url'], i['attachment']['url'], i['attachment']['title'], i['attachment']['description']))
					else:
						c.execute("INSERT INTO comments (date, name, userid, message, id, type, target_id, target_url, url, title, description) VALUES (?,?,?,?,?,?,?,?,?,?,?);", (i['created_time'], i['from']['name'], i['from']['id'], i['message'], i['id'], i['attachment']['type'], i['attachment']['target']['id'], i['attachment']['target']['url'], i['attachment']['url'], i['attachment']['title'], i['attachment']['description']))
				else:
					c.execute("INSERT INTO comments (date, name, userid, message, id, type, media_image_src, media_image_width, media_image_height, target_id, target_url, url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);", (i['created_time'], i['from']['name'], i['from']['id'], i['message'], i['id'], i['attachment']['type'], i['attachment']['media']['image']['src'], i['attachment']['media']['image']['width'], i['attachment']['media']['image']['height'], i['attachment']['target']['id'], i['attachment']['target']['url'], i['attachment']['url']))
			else:
				c.execute("INSERT INTO comments (date, name, userid, message, id) VALUES (?,?,?,?,?);", (i['created_time'], i['from']['name'], i['from']['id'], i['message'], i['id']))
		except:
			print(i)
			raise
		date_tmp = i['created_time']
	dbc.commit()
	sys.stderr.write('Fetched ' + str(cnt*size) + ' comments - ' + date_tmp + '\n')
	url = data['paging']['next']