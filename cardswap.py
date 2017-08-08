#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect
import json, os, requests, re, sys

basepath = os.path.dirname(sys.executable)
cardpath = os.path.join(basepath, "card0.txt")
datapath = os.path.join(basepath, "cards.json")

app = Flask(__name__, root_path = basepath)

chosen = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global chosen
    if request.method == 'POST':
        new_card(request.form['name'], request.form['card_id'], request.form['display_id'], request.form.getlist('autofill'))
    return render_template('cardswap.html', list=read_cards(), chosen=chosen, admin=False)

@app.route('/card_<id>', methods=['GET', 'POST'])
def select_card(id):
    global chosen
    chosen = id
    createtxt(id)
    return redirect('/')

@app.route('/delete_<i>', methods=['GET', 'POST'])
def delete_card(i):
    filtered = [d for d in read_cards() if d['id'] != i]
    write_cards(filtered)
    return redirect('/')

def new_card(name, id, disp, fill):
    l = read_cards()
    if fill:
        if len(id) == 0:
            id = dispID2cardID(disp)
        if len(disp) == 0:
            disp = cardID2dispID(id)
    if id and disp:
        l.append({'name': name, 'id': id, 'disp': disp})
    write_cards(l)

def createtxt(id, path=cardpath):
    with open(path, mode='w') as fp:
        fp.write(id)

def read_cards(fname = datapath):
    """return list of card dicts"""
    if os.path.isfile(fname):
        with open(fname, mode='r') as fp:
            j = json.load(fp)
            return j
    else:
        return []

def write_cards(l, fname = datapath):
    with open(fname, mode='w') as fp:
        json.dump(l, fp)

def dispID2cardID(id):
    # curl 'http://quasar.me/card.php' --data card_id=G3E0LZCD3SCU1016
    r = requests.post('http://quasar.me/card.php', data = {'card_id' : id})
    match = re.search('Your internal ID is ([^\.]*)\.', r.text).groups()[0]
    print("matched {} to {}".format(id, match))
    if match in ['null', 'invalid']:
        return None
    else:
        return match

def cardID2dispID(id):
    # curl 'http://quasar.me/card.php' --data rfid=E00401002DE879A9
    r = requests.post('http://quasar.me/card.php', data = {'rfid' : id})
    match = re.search('Your card ID is ([^\.]*)\.', r.text).groups()[0]
    print("matched {} to {}".format(id, match))
    if match in ['null', 'invalid']:
        return None
    else:
        return match

if __name__ == '__main__':
    if os.path.isfile(cardpath):
        with open(cardpath) as fp:
            chosen = fp.read()
    app.run(host = '0.0.0.0', use_evalex=False)
