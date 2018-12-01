from APIOpenBD import APIOpenBD
from ElasticsearchWrapper import ElasticsearchWrapper
from flask import Flask, render_template, request, jsonify
import json
from jinja2 import Template, Environment, FileSystemLoader

import re

from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


class CustomFlask(Flask):
    '''
    テンプレートのデリミタがVue.jsと競合するので、Flask側でデリミタを別の文字に変更する
	参照：https://muunyblue.github.io/0b7acbba52fb92b2e9c818f7f56bac99.html
    '''
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
		block_start_string='(%',
		block_end_string='%)',
		variable_start_string='((',
		variable_end_string='))',
		comment_start_string='(#',
		comment_end_string='#)',
    ))

    template_filter = Flask.template_filter


app = CustomFlask(__name__)
#app = Flask(__name__)

# @app.template_filter()
# @evalcontextfilter
@app.template_filter('nl2br')
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

@app.template_filter('linebreaksbr')
def linebreaksbr(arg):
    return arg.replace("\n", "<br />\n")

# env = Environment(loader=FileSystemLoader('.'), trim_blocks=False)

# env.filters['linebreaksbr'] = linebreaksbr
# template = env.get_template('index.html')

# env.filters.update({
# 	"linebreaksbr": jinja2_custom_filters.linebreaksbr,
# })

app.config['JSON_AS_ASCII'] = False    # jsonifyで日本語が文字化けする場合の対処


@app.route("/")
def index():
	'''
	画面
	'''
	return render_template("index.html")
	# return template.render("index.html")

@app.route("/get")
def get():
	'''
	ISBNに対応する書籍情報の取得
	'''
	# パラメータからISBNコードを取得
	isbn = request.args.get('isbn', default=None)
	# 必要な情報を取得する
	json_data = APIOpenBD().get_json(isbn) if isbn else {}
	# dict型をJSON型のレスポンスに変換
	response = jsonify(json_data)

	return response

@app.route("/regist")
def regist():
	'''
	ISBNに対応する書籍情報を取得して、Elasticsearchに登録
	'''
	# パラメータからISBNコードを取得
	isbn = request.args.get('isbn', default=None).replace('-','')
	# 必要な情報を取得する
	json_data = APIOpenBD().get_json(isbn) if isbn else {}

	if json_data == None:
		json_data = {}
	
	if len(json_data) > 0:
		# Elasticsearch
		es = ElasticsearchWrapper('openbd', 'openbd-index')
		# 追加
		es.insert_one(json_data)

	# dict型をJSON型のレスポンスに変換
	response = jsonify(json_data)

	return response

@app.route("/search")
def search():
	'''
	検索
	'''
	# パラメータからISBNコードを取得
	isbn = request.args.get('isbn', default=None)
	title = request.args.get('title', default=None)
	author = request.args.get('author', default=None)
	publisher = request.args.get('publisher', default=None)
	publishedDate = request.args.get('publishedDate', default=None)
	description = request.args.get('description', default=None)

	# 検索の項目名、項目値のDictionary
	items = {}
	if isbn != None:
		items['isbn'] = isbn.replace('-','')
	if title != None:
		items['title'] = title
	if author != None:
		items['authors'] = author
	if publisher != None:
		items['publisher'] = publisher
	if publishedDate != None:
		items['publishedDate'] = publishedDate
	if description != None:
		items['description'] = description

	# Elasticsearch
	es = ElasticsearchWrapper('openbd', 'openbd-index')
	# 検索
	json_data = es.search_and(items)

	# dict型をJSON型のレスポンスに変換
	response = jsonify(json_data)

	return response

if __name__ == "__main__":
    print(linebreaksbr('aaa\nbbb'))
    app.run(debug=False, host='0.0.0.0', port=8080)
