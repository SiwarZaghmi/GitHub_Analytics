import requests
import pymongo
#from pymongo import mongo_client

url = 'https://api.github.com/repos/SiwarZaghmi/GitHub_Analytics/issues'
response = requests.get(url)
data = response.json()
#print (data)

def delete_issue_information(data):
 for issue in data :
    del issue['repository_url']
    del issue['labels_url']
    del issue['comments_url']
    del issue['events_url']
    del issue['html_url']
    del issue['timeline_url']
    del issue['active_lock_reason']
    del issue['assignee']
    del issue['user']
    del issue['author_association']
    del issue['reactions']
    del issue['performed_via_github_app']

# Nettyotage des donneés du labels

def clean_labels(j):
    for issue in j:
        labels = issue['labels']
        for label in labels:
             del label['default']

def clean_assignees(j):
    for issue in j:
        assignees = issue['assignees']
        for assignee in assignees:
            del assignee['html_url']
            del assignee['followers_url']
            del assignee['gists_url']
            del assignee['starred_url']
            del assignee['subscriptions_url']
            del assignee['organizations_url']
            del assignee['received_events_url']
            del assignee['gravatar_id']
            del assignee['url']


#print(data)
#appel des fonctions
clean_labels(data)
clean_assignees(data)
delete_issue_information(data)
print(data[6])


client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb = client['GitHubProject']

info = mydb.issues
info.insert_many(data)

"""

info1 = mydb.events
info1.insert_many(ev)
"""
