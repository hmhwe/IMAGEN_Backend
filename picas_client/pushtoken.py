import sys
import os
import couchdb
import random
import picasconfig
import json


def getNextIndex():
    db = get_db()

    index = 0
    while db.get(f"token_{index}") is not None:
        index+=1

    return index

def loadTokens(db, tokensfile):
    with open(tokensfile) as f:
        tokens = json.load(f)

    i = getNextIndex()
    for token in tokens:
        token['_id'] = f'token_{i}'
        i += 1

    db.update(tokens)

def get_db():
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username,pwd)
    db = server[picasconfig.PICAS_DATABASE]
    return db

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python pushtoken.py <tokensfile>")
        sys.exit(1)

    tokensfile = sys.argv[1]
    # Create a connection to the server
    db = get_db()
    
    # Load the tokens from the JSON file
    loadTokens(db, tokensfile)