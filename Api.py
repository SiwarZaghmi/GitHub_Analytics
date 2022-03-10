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
       elif  data['action'] == "closed" or data['action'] == "edited":
           issue = issues_collection.find_one({'node_id': data['issue']['node_id']})
           if issue:
            issues_collection.update_one({'node_id': data['issue']['node_id']},
                                              {"$set": {'state': data['issue']['state'],
                                                        'updated_at' : data['issue']['updated_at'],
                                                        'closed_at': data['issue']['closed_at'],
                                                        'title': data['issue']['title'],
                                                        'body': data['issue']['body'],
                                                           }})
            return ("ok")
           else : return abort(404, description="issue not found")

       elif data['action'] == "deleted" :
          issue = issues_collection.find_one({'node_id': data['issue']['node_id']})
          if issue:
              # jointure
           issue_del = {"id": data['issue']['node_id']}
           info_del = {"issue_id" : data['issue']['node_id']}
           issues_collection.delete_one(issue_del)
           labels_collection.delete_many(info_del)
           assigness_collection.delete_many(info_del)
           project_card_collection.delete_one(info_del)
           return ("ok")
          else:
             return abort(404, description="issue not found")


       elif data['action'] == "labeled":
         label = labels_collection.find_one({'id': data['label']['id']})
         if not label:
             label = data['label']
             name = label['name'].lower()
             if name[0:4] == "size" or name[0:4] == "epic":
                 try:
                     name1 = name.replace(" ", "")
                     nv = name1.split(":")
                     print(nv[0])
                     labels_collection.insert_one({
                         'id': label['id'],
                         'issue_id': data['issue']['node_id'],
                         'description': label['description'],
                         'name': nv[0],
                         'value': nv[1]
                     })
                 except IndexError:
                     print('only one value')
                 return("ok")
             elif name[0:5] == "logged":
                 try:
                     name1 = name.replace(" ", "")
                     nv = name1.split(":")
                     labels_collection.insert_one({
                         'id': label['id'],
                         'issue_id': data['issue']['node_id'],
                         'description': label['description'],
                         'name': nv[0],
                         'value': nv[1]
                     })
                 except IndexError:
                     print('only one value')
                 return ('ok')

             else:
                 labels_collection.insert_one({
                     'id': label['id'],
                     'issue_id': data['issue']['node_id'],
                     'description': label['description'],
                     'name': label['name'],
                     'value': 'null'
                 })
             return ('ok')
         else:
          return abort(404, description="label can not be added")
       elif data['action'] == "unlabeled":
         label = labels_collection.find_one({'issue_id': data['issue']['node_id']})
         if label:
            myquery = {"id": data['label']['id']}
            labels_collection.delete_one(myquery)
            return ("ok")
         else:
             return abort(404, description="label Not Found")


       # opened, edited, deleted, pinned, unpinned, closed, reopened, assigned
       # unassigned, labeled, unlabeled, locked, unlocked, transferred, milestoned,
       # or demilestoned.

       elif data['action'] == "assigned":
           assignee = assigness_collection.find_one({'issue_id': data['issue']['node_id']
                                                     })
           if not assignee:
            assigness_collection.insert_one({
                'login': data['assignee']['login'],
               'issue_id': data['issue']['node_id'],
               'id': data['assignee']['id']


           })
            return("ok")
           else:
               return abort(404, description="assigne can not be added")


       elif data['action'] == "unassigned":
           assignee = assigness_collection.find_one({'issue_id': data['issue']['node_id']})
           if assignee:
            myquery = {"issue_id": data['issue']['node_id']}
            assigness_collection.delete_one(myquery)
            return ("ok")
           else:

               return abort(404, description="assigne not found")
       # opened, edited, deleted, pinned, unpinned, closed, reopened, assigned
       # unassigned, labeled, unlabeled, locked, unlocked, transferred, milestoned,
       # or demilestoned.



       else: return("bug")
