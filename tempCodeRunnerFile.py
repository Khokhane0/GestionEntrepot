from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.secret_key = 'secretkey'

# MongoDB Connection URL
uri= "mongodb+srv://papekhokhanesene:<ABcd77-+>@cluster0.41qkl.mongodb.net/"

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['final']
collection = db['immigration']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        country = request.form.get('country')
        continent = request.form.get('continent')
        region = request.form.get('region')

        # Query MongoDB
        results = collection.find({
            'Country': {'$regex': country, '$options': 'i'},
            'Continent': {'$regex': continent, '$options': 'i'},
            'Region': {'$regex': region, '$options': 'i'}
        })
        return render_template('search.html', results=results)

    return render_template('search.html', results=None)

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        country = request.form.get('country')

        # Fetch record from MongoDB
        record = collection.find_one({'Country': {'$regex': country, '$options': 'i'}})
        if record:
            return render_template('update.html', record=record)
        else:
            flash("Country not found!")
            return redirect(url_for('update'))

    return render_template('update.html', record=None)

@app.route('/update_action', methods=['POST'])
def update_action():
    country = request.form.get('country')
    new_data = {
        'Continent': request.form.get('continent'),
        'Region': request.form.get('region')
    }

    # Update MongoDB record
    collection.update_one({'Country': country}, {'$set': new_data})
    flash("Information updated successfully!")
    return redirect(url_for('update'))

@app.route('/delete', methods=['POST'])
def delete():
    country = request.form.get('country')
    # Delete record
    collection.delete_one({'Country': country})
    flash("Record deleted successfully!")
    return redirect(url_for('update'))

if __name__ == '__main__':
    app.run(debug=True)