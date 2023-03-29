#!/usr/bin/env python3

# Version 1.0.5
# Author: Synfinner
# Site: https://gtfkd.com

from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from flask import redirect
from flask import make_response
from flask import jsonify
import sqlite3
from werkzeug.exceptions import abort
import datetime
import io
import csv
import os.path
import create_db

# Establish SQLITE db connection and return it. 
def get_db_connection():
    conn = sqlite3.connect('data/intlog.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.config['SECRET_KEY'] = 'WTFAMIDOINGWITHMYLIFE'

# Function to get all the investigation IDs 
def get_inv(inv_id):
    conn = get_db_connection()
    investigation = conn.execute('SELECT * FROM investigations WHERE id = ?',
                        (inv_id,)).fetchone()
    conn.close()
    if investigation is None:
        abort(404)
    return investigation

# Function to get all artifact entries in descending order by date
def get_artifacts(inv_id):
    conn = get_db_connection()
    artifacts = conn.execute('SELECT * FROM artifacts WHERE investigation_id = ? ORDER BY artifact_date DESC',
                        (inv_id,)).fetchall()
    conn.close()
    if artifacts is None:
        abort(404)
    return artifacts

# Redundant function to get artifact entries in ascending order by date
def get_artifacts_date_asc(inv_id):
    conn = get_db_connection()
    artifacts = conn.execute('SELECT * FROM artifacts WHERE investigation_id = ? ORDER BY artifact_date ASC',
                        (inv_id,)).fetchall()
    conn.close()
    if artifacts is None:
        abort(404)
    return artifacts

# Broad function to get all artifacts
def get_artifact(article_id):
    conn = get_db_connection()
    artifacts = conn.execute('SELECT * FROM artifacts WHERE id = ?',
                        (article_id,)).fetchone()
    conn.close()
    if artifacts is None:
        abort(404)
    return artifacts

# Function to get all available artifact types. Used for dropdown to add new artifacts
def get_types():
    conn = get_db_connection()
    types = conn.execute('SELECT * FROM types ORDER BY type ASC').fetchall()
    conn.close()
    if types is None:
        abort(404)
    return types

# Route and function to get a timeline of artifacts per investigation
@app.route('/<int:inv_id>/timeline')
def timeline(inv_id):
    artifacts = get_artifacts_date_asc(inv_id)
    investigation = get_inv(inv_id)
    return render_template('timeline.html', investigation=investigation,artifacts=artifacts)

# Function/route to return all artifacts in JSON format per investigation
@app.route('/json_exp/<int:inv_id>')
def json_exp(inv_id):
    conn = get_db_connection()
    artifacts = conn.execute('SELECT * FROM artifacts WHERE investigation_id = ?',
                        (inv_id,)).fetchall()
    conn.close()
    if artifacts is None:
        abort(404)
    data = []
    for row in artifacts:
        data.append({'id':row[0],'artifact_type':row[3],'artifact_description':row[4],'artifact':row[5],'date_added':row[6],'flagged':row[7]})
    return jsonify(data)

# Function/Route to create a new investigation
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        inv_name = request.form['investigation_name']
        inv_desc = request.form['investigation_description']
        date = datetime.datetime.now().replace(microsecond=0).isoformat()
        if not inv_name:
            flash('Investigation name is required!!!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO investigations (investigation_name, investigation_date, investigation_desc) VALUES (?, ?, ?)',
                         (inv_name, date, inv_desc))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

# Function/Route to add an artifact to an investigation
@app.route('/<int:inv_id>/add_artifact',methods=('GET', 'POST'))
def add_artifact(inv_id):
    if request.method == 'POST':
        artifact_type = request.form['type']
        artifact_data = request.form['artifact_data']
        artifact_desc = request.form['artifact_description']
        date = datetime.datetime.now().replace(microsecond=0).isoformat()
        if not artifact_data:
            flash('An artifact is required!!!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO artifacts (artifact_type, artifact_reference, artifact_desc, investigation_id, artifact_date) VALUES (?, ?, ?, ?, ?)',
                         (artifact_type, artifact_data, artifact_desc,inv_id,date))
            conn.commit()
            conn.close()
            return redirect(url_for('investigation',inv_id = inv_id))
    types = get_types()
    return render_template('add_artifact.html',types=types)

# Function to get artifacts from an infestigation and export as CSV
@app.route('/<int:inv_id>/export_artifacts',methods=('GET',))
def export_artifacts(inv_id):
    conn = get_db_connection()
    rows = conn.execute('SELECT artifact_reference, artifact_type, artifact_desc, artifact_date FROM artifacts WHERE investigation_id = ?',
                         (inv_id,)).fetchall()
    conn.close()
    # Add error handling if there are no artifacts
    if not rows:
        flash('No artifacts found for this investigation!')
        return redirect(request.referrer)
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(rows)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=artifact_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# Function/route to delete an artifact. 
@app.route('/delete_artifact/<int:artifact_id>',methods=('GET',))
def delete_artifact(artifact_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM artifacts WHERE id = ?', (artifact_id,))
    conn.commit()
    conn.close()
    flash("Removed artifact!")
    return redirect(request.referrer)

# Function/Route to add a flag to an artifact entry
@app.route('/add_flag/<int:artifact_id>', methods=('GET',))
def add_flag(artifact_id):
    conn = get_db_connection()
    conn.execute('UPDATE artifacts SET flagged=? WHERE id=?',(1,artifact_id))
    conn.commit()
    return redirect(request.referrer)

# Function/Route to remove a flag. Seperated for ease. 
@app.route('/rem_flag/<int:artifact_id>', methods=('GET',))
def rem_flag(artifact_id):
    conn = get_db_connection()
    conn.execute('UPDATE artifacts SET flagged=? WHERE id=?',(0,artifact_id))
    conn.commit()
    return redirect(request.referrer)

# Function/Route to delete an entire investigation
@app.route('/delete_investigation/<int:inv_id>',methods=('POST','GET'))
def delete_investigation(inv_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM investigations WHERE id = ?', (inv_id,))
    conn.commit()
    try:
        conn.execute('DELETE FROM artifacts WHERE investigation_id = ?', (inv_id,))
        conn.commit()
    except:
        pass
    conn.close()
    flash('Deleted investigation!')
    return redirect(url_for('index'))

# Function/Route to archive an investigation
@app.route('/archive_inv/<int:inv_id>', methods=('GET',))
def archive_inv(inv_id):
    conn = get_db_connection()
    conn.execute('UPDATE investigations SET investigation_archived=? WHERE id=?',(1,inv_id))
    conn.commit()
    return redirect(request.referrer)

# Function/Route to unarchive an investigation
@app.route('/unarchive_inv/<int:inv_id>', methods=('GET',))
def unarchive_inv(inv_id):
    conn = get_db_connection()
    conn.execute('UPDATE investigations SET investigation_archived=? WHERE id=?',(0,inv_id))
    conn.commit()
    return redirect(request.referrer)

# Function/Route to edit an artifact item
@app.route('/edit_artifact/<int:artifact_id>',methods=('POST','GET'))
def edit_artifact(artifact_id):
    args = request.args
    artifact = get_artifact(artifact_id)
    types = get_types()
    if request.method == 'POST':
        artifact_type = request.form['type']
        artifact_data = request.form['artifact_data']
        artifact_desc = request.form['artifact_description']
        if not artifact_data:
            flash('An artifact is required!!!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE artifacts SET artifact_type=?, artifact_reference=?, artifact_desc=? WHERE id = ?',
                         (artifact_type, artifact_data, artifact_desc,artifact_id))
            conn.commit()
            conn.close()
            if len(args) > 0:
                return redirect(url_for('investigation',inv_id = args['inv_id']))
            else:
                return redirect(url_for('index'))
    return render_template('edit_artifact.html',artifact=artifact, types=types)

# FunctionRoute for viewing an investigation
@app.route('/<int:inv_id>')
@app.route('/<int:inv_id>/')
def investigation(inv_id):
    investigation = get_inv(inv_id)
    artifacts = get_artifacts(inv_id)
    return render_template('investigation.html', investigation=investigation,artifacts=artifacts)

# Function/Route to load the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Function/Route to view the archive and associated items
@app.route('/archive')
def archive():
    conn = get_db_connection()
    investigations = conn.execute('SELECT * FROM investigations WHERE investigation_archived == 1 ORDER BY investigation_date DESC').fetchall()
    #print(investigations)
    conn.close()
    return render_template('archive.html',investigations=investigations) 

# Function/Route for the index page
@app.route('/')
def index(page=1):
    conn = get_db_connection()
    investigations = conn.execute('SELECT * FROM investigations WHERE investigation_archived == 0 OR investigation_archived IS NULL ORDER BY investigation_date DESC').fetchall()
    conn.close()
    return render_template('index.html',investigations=investigations)

# Function for handling 404 errors instead of just breaking.
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# Function for initial DB creation
def checkdb():
    if os.path.isfile('data/intlog.sqlite'):
        pass
    else:
        create_db.create_db()

if __name__ == "__main__":
    # Perform DB creation check.
    checkdb()
    # Run the app.
    app.run()
