import requests
import pymongo
token = "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"
headers = { 'Authorization' : "token {}". format(token)}
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb = client['GitHubProject']
# les collections
issues_collection = mydb.issues
labels_collection = mydb.labels
project_card_collection = mydb.project_cards
assigness_collection = mydb.assignees
milestone_collection = mydb.milestones
#get project
project = requests.get('https://api.github.com/projects/14134007/columns', headers = headers).json()
#parcourir les colonnes


for column in project:

 column_name = column['name']
 print( column['name'])
 cards = requests.get(column['cards_url'], headers=headers).json()
 try:
   for card in cards:
       content = card['content_url']
       issue = requests.get(content, headers=headers).json()

       issues_collection.insert_one({
               'id': issue['id'],
               'node_id': issue['node_id'],
               'number': issue['number'],
               'title': issue['title'],
               'state': issue['state'],
               'locked': issue['locked'],
               'created_at': issue['created_at'],
               'updated_at': issue['updated_at'],
               'closed_at': issue['closed_at'],
               'body': issue['body']

           })
           labels = issue['labels']
       for label in labels:
           name = label['name'].lower()

           if name[0:4] == "size" or name[0:4] == "epic":
             try:
               name1 = name.replace(" ","")
               nv = name1.split(":")

               print(nv[0])
               labels_collection.insert_one({
               'id': label['id'],
               'issue_id': issue['node_id'],
               'description': label['description'],
               'name': nv[0],
               'value': nv[1]
           })
             except IndexError:
                 print('only one value')
           elif name[0:5] == "logged":
             try:
               name1 = name.replace(" ", "")
               nv = name1.split(":")
               labels_collection.insert_one({
                   'id': label['id'],
                   'issue_id': issue['node_id'],
                   'description': label['description'],
                   'name': nv[0],
                   'value': nv[1]
               })
             except IndexError:
               print('only one value')
           else:
               labels_collection.insert_one({
                   'id': label['id'],
                   'issue_id': issue['node_id'],
                   'description': label['description'],
                   'name': label['name'],
                   'value': 'null'
               })


       project_card_collection.insert_one({
           'issue_id': issue['node_id'],
           'card_name': column_name,
           'id': card['id'],
       })
