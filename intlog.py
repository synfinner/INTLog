#!/usr/bin/env python3

from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from flask import redirect
from flask import make_response
from flask_fontawesome import FontAwesome
import sqlite3
from werkzeug.exceptions import abort
import datetime
import io
import csv

def get_db_connection():
    conn = sqlite3.connect('data/intlog.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.config['SECRET_KEY'] = 'WTFAMIDOINGWITHMYLIFE'
fa = FontAwesome(app)

def get_inv(inv_id):
    conn = get_db_connection()
    investigation = conn.execute('SELECT * FROM investigations WHERE id = ?',
                        (inv_id,)).fetchone()
    conn.close()
    if investigation is None:
        abort(404)
    return investigation

def get_artifacts(inv_id):
    conn = get_db_connection()
    artifacts = conn.execute('SELECT * FROM artifacts WHERE investigation_id = ? ORDER BY artifact_date DESC',
                        (inv_id,)).fetchall()
    conn.close()
    if artifacts is None:
        abort(404)
    return artifacts

def get_artifact(article_id):
    conn = get_db_connection()
    artifacts = conn.execute('SELECT * FROM artifacts WHERE id = ?',
                        (article_id,)).fetchone()
    conn.close()
    if artifacts is None:
        abort(404)
    return artifacts

def get_types():
    conn = get_db_connection()
    types = conn.execute('SELECT * FROM types ORDER BY type ASC').fetchall()
    conn.close()
    if types is None:
        abort(404)
    return types

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

@app.route('/<int:inv_id>/add_artifact',methods=('GET', 'POST'))
def add_artifact(inv_id):
    if request.method == 'POST':
        #artifact = request.form['artifact']
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

@app.route('/<int:inv_id>/export_artifacts',methods=('GET', 'POST'))
def export_artifacts(inv_id):
    conn = get_db_connection()
    si = io.StringIO()
    cw = csv.writer(si)
    rows = conn.execute('SELECT artifact_reference, artifact_type, artifact_desc, artifact_date FROM artifacts WHERE investigation_id = ?',
                        (inv_id,)).fetchall()
    cw.writerows(rows)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=artifact_export.csv"
    output.headers["Content-type"] = "text/csv"
    conn.close()
    return output

@app.route('/delete_artifact/<int:artifact_id>',methods=('POST','GET'))
def delete_artifact(artifact_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM artifacts WHERE id = ?', (artifact_id,))
    conn.commit()
    conn.close()
    flash("Removed artifact!")
    return redirect(request.referrer)

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

@app.route('/edit_artifact/<int:artifact_id>',methods=('POST','GET'))
#@app.route('/investigation/<int:inv_id>/edit_artifact/<int:artifact_id>',methods=('POST','GET'))
def edit_artifact(artifact_id):
    args = request.args
    artifact = get_artifact(artifact_id)
    types = get_types()
    if request.method == 'POST':
        #artifact = request.form['artifact']
        artifact_type = request.form['type']
        artifact_data = request.form['artifact_data']
        artifact_desc = request.form['artifact_description']
        #date = datetime.datetime.now().replace(microsecond=0).isoformat()
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


@app.route('/<int:inv_id>')
def investigation(inv_id):
    investigation = get_inv(inv_id)
    artifacts = get_artifacts(inv_id)
    return render_template('investigation.html', investigation=investigation,artifacts=artifacts)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
#@app.route('/page/<int:page>')
def index(page=1):
    #return "wtf"
    conn = get_db_connection()
    investigations = conn.execute('SELECT * FROM investigations ORDER BY investigation_date DESC').fetchall()
    #print(investigations)
    conn.close()
    return render_template('index.html',investigations=investigations)


if __name__ == "__main__":
    app.run()
