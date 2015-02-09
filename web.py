# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from flask import Flask, render_template, session, redirect, url_for, escape, request, Response
app = Flask(__name__)

import search
import index

indexer = index.indexer()

def StartWeb(shouldDebug=False):
	app.debug=shouldDebug
	app.secret_key = "asdfasdfasdF"
	app.run(host='0.0.0.0')

	
def runSearch(getArgs):
	q=getArgs("q")
	s = search.search(indexer, q)
	return s.Write()

@app.route('/')
def home():
	return render_template('homepage.html')
	
@app.route('/search/', methods=['GET', 'POST'])
def searchPage():
	return runSearch(request.args.get)
	
StartWeb(False)