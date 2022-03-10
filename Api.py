import pymongo
from flask import json
from flask import request
from flask import Flask
from flask import abort
import requests

app = Flask(__name__)



#1 connexion bdd

@app.route('/git' , methods=['POST'])
def webhook():
   token = "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"
   headers = {'Authorization': "token {}".format(token)}
   client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
   mydb = client['GitHubProject']
    # les collections
   issues_collection = mydb.issues
   labels_collection = mydb.labels
   project_card_collection = mydb.project_cards
   assigness_collection = mydb.assignees
   data = request.json
   if request.headers['X-GitHub-Event'] == 'issues':
       if data['action'] == "opened":
         issue = issues_collection.find_one({'id': data['issue']['node_id']})
         if not issue:
           issues_collection.insert_one({
             'id': data['issue']['id'],
             'node_id': data['issue']['node_id'],
             'number': data['issue']['number'],
             'title': data['issue']['title'],
             'state': data['issue']['state'],
             'locked': data['issue']['locked'],
             'created_at': data['issue']['created_at'],
             'updated_at': data['issue']['updated_at'],
             'closed_at': data['issue']['closed_at'],
             'body': data['issue']['body'],
             #'id_milestone': data['issue']['milestone']['node_id']
           })
           labels = data['issue']['labels']
           for label in labels:
             labels_collection.insert_one({
               'id': label['id'],
               'issue_id': data['issue']['node_id'],
               'description': labels['description'],
               'name': label['name']

           })
           assigness = data['issue']['assignees']
           for assigne in assigness:
              assigness_collection.insert_one({
               'login': assigne['login'],
               'issue_id': assigne['node_id'],
               'id': assigne['id']
              })
           return("ok")
         else :
           return abort(404, description="issue existe")
