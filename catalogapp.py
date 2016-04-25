from flask import Flask, render_template, request,\
    redirect, url_for, jsonify, session as login_session, make_response, flash
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categorie, CategorieItem
from oauth2client.client  import flow_from_clientsecrets
from oauth2client.client  import FlowExchangeError
import httplib2
import json
import requests

import random, string

__author__ = 'Luka Ivkic'

app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "CatalogApp1"

engine = create_engine('sqlite:///item.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON API Get list of all categories
@app.route('/category/JSON')
def categorie_json():
    categorie = session.query(Categorie).all()
    return jsonify(Categorie= [r.serialize for r in categorie])

# JSON API Get items for specific categorie
@app.route('/category/<int:categorie_id>/item/JSON')
def categorie_item_json(categorie_id):
    categorie = session.query(Categorie).filter_by(id=categorie_id).one()
    items = session.query(CategorieItem).filter_by(categorie_id=categorie.id).all()
    return jsonify(CategorieItem=[i.serialize for i in items])

# The root of the application
@app.route('/')
def open_catalog():
    categories = session.query(Categorie).order_by(Categorie.id)
    # We will return the list of last added items in the database limit it to 10 records
    s = session.query(CategorieItem, Categorie).join(Categorie).order_by(desc(CategorieItem.dateCreated)).limit(10)
    return render_template('list_top_item.html', items=s, categories=categories)

# Call for login logic
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']

    return redirect(url_for('open_catalog'))

# Use Google + to login
@app.route('/gdisconnect', methods=['GET', 'POST'])
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        print "OK"
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('User loged out')
        return redirect(url_for('open_catalog'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Delete existing item
@app.route("/catalog/<name>/deleteItem", methods=['GET', 'POST'])
def delete_item(name):
    if request.method == 'POST':
        if request.form['submit'] == 'Delete':
            item_to_delete = session.query(CategorieItem).filter_by(name=name).one()
            session.delete(item_to_delete)
            session.commit()
            return redirect(url_for('open_catalog'))
        elif request.form['submit'] == 'Cancel':
            return redirect(url_for('open_catalog'))
    else:
        item = session.query(CategorieItem).filter_by(name=name).one()
        return render_template('delete_item.html', item=item)

# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Add new item
@app.route("/catalog/<name>/addItem", methods=['GET', 'POST'])
def add_item(name):
    # if not authorized go to root
    if 'username' not in login_session:
        return redirect(url_for('open_catalog'))

    if request.method == 'POST':
        if request.form['submit'] == 'Cancel':
            return redirect(url_for('open_catalog'))
        else:
            if request.form['name'] == '':
                # if empty redirect
                return redirect(url_for('open_catalog'))

            categories = session.query(Categorie).filter_by(name=name).one()
            new_item = CategorieItem(name=request.form['name'], description=request.form['desti'],
                                     categorie_id=categories.id)
            session.add(new_item)
            session.commit()
            return redirect(url_for('open_catalog'))
    elif request.method == 'GET':
        print name
        categories = session.query(Categorie).order_by(Categorie.id)
        return render_template('add_item.html', name=name, categories=categories)

# Edit existing record
@app.route("/catalog/<name>/edit", methods=['GET', 'POST'])
def edit_item(name):
    # if not authorized redirect
    if 'username' not in login_session:
        return redirect(url_for('open_catalog'))

    print request.method
    if request.method == 'POST':
        # if Cancel is pressed redirect to main page
        if request.form['submit'] == 'Cancel':
            return redirect(url_for('open_catalog'))
        elif request.form['submit'] == 'Save':
            if request.form['name'] == '':
                # if empty redirect
                return redirect(url_for('open_catalog'))

            categorie = session.query(Categorie).filter_by(name=request.form['categories']).one()
            c = session.query(CategorieItem).filter_by(name=name).one()
            c.name = request.form['name']
            c.description = request.form['desti']
            c.categorie_id = categorie.id
            session.add(c)
            session.commit()
            return redirect(url_for('open_catalog'))
    elif request.method == 'GET':
        # If get let fill the data that we need
        categories = session.query(Categorie).order_by(Categorie.id)
        c = session.query(CategorieItem).filter_by(name=name).one()
        item_category = session.query(Categorie).filter_by(id=c.categorie_id).one()
        return render_template('edit_item.html', catalogitem=c, categories=categories, item_category=item_category)

# Show items in category
@app.route('/catalog/<string:name>/items')
def item_catalog(name):
    categories = session.query(Categorie).order_by(Categorie.id)
    c = session.query(CategorieItem).join(Categorie).filter(
        Categorie.name == name).all()
    return render_template('category_item.html', categories=categories, catalogitem=c, name=name)

# Show details information about item
@app.route('/catalog/<string:categories>/<string:name>')
def item_details(categories, name):
    print "item_details"
    c = session.query(CategorieItem).filter_by(name=name).one()
    print c.name
    print c.description
    return render_template('item_details.html', catalogitem=c, categories=categories)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'my_secret_key'
    app.run(host='0.0.0.0', port=8000)
