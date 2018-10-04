#!/usr/bin/env python

import flask
from flask import Response, request, send_file, flash
import json
import sqlite3
import csv
from config import Config
from contactform import ContactForm


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
# from flask_wtf.csrf import CSRFProtect
# from flask_mail import Message, Mail

app = flask.Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
#app.config['TESTING'] = True

# mail = Mail()
# app.secret_key = 'development key'
#
# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_USERNAME"] = 'contact@example.com'
# app.config["MAIL_PASSWORD"] = 'your-password'
#
# mail.init_app(app)

@app.route('/')
def index():
	"""
	Displays the home page that leads users into different pages
	"""
	return flask.render_template('index.html')

@app.route('/about')
def about():
	return flask.render_template('about.html')

@app.route('/process')
def process():
	return flask.render_template('process.html')

@app.route('/team')
def team():
	return flask.render_template('team.html')

# @app.route('/contact', methods=["GET", "POST"])
# def contact():

# 	if request.method == 'POST':
# 		email = request.form.get('email')
# 		name = request.form.get('message')
# 		subject = request.form.get('subject')
# 		message = request.form.get("message")
# 		#send_email(message, reply_to)
# 		return flask.render_template('contact.html', success=True)
# 	else:

		# return flask.render_template('contact.html', success=False, message_type=message_type)


# 	return flask.render_template('contact.html', message_type=message_type)

@app.route('/contact', methods=["GET", "POST"])
def contact():
	form = ContactForm()
	message_type = ["More Information about Goodly Labs",
	"Potential Errors in the Dataset", "Suggestions", "Questions and Concerns", "Other"]
	if form.validate_on_submit():

		email = request.form.get('email')
		name = request.form.get('name')
		subject = request.form.get('subject')
		message = request.form.get("message")
		body = "Name: " + name + "\nEmail: " + email + "\n\nSubject: " + subject + "\n\nBody: " + message + "\n\n"

		#print("RETRIEVED")

		msg_for_us = Message(subject="Searchlight Contact Form Submission", sender=app.config.get("MAIL_USERNAME"),
					recipients=["omkar.waingankar@berkeley.edu", "nalinchopra123@gmail.com"],
					body=body)
		mail.send(msg_for_us)

		msg_for_sender = Message(subject="Searchlight Contact Form Receipt", sender=app.config.get("MAIL_USERNAME"),
					recipients=[email],
					body="Hi " + name + ",\n\n" + "Thanks for connecting with us. " +
					"We'll be sure to get back in touch with you as soon as possible!\n\n" +
					"Contact Form Receipt: \n\n" + body +
					"Best,\nThe Searchlight Team")

		mail.send(msg_for_sender)

		#print("MESSAGE SENT BY " + name)

		return flask.render_template('contact.html', title='Submitted', success=True)

	return flask.render_template('contact.html', title='Contact Us', form=form, message_type=message_type, success=False)

@app.route('/query')
def speakers():

	month_dict = {'January': '1', 'February': '2', 'March': '3', 'April': '4', 'May': '5', 'June': '6', 'July': '7',
             'August': '8', 'September': '9', 'October': '10', 'November': '11', 'December': '12'}

	format_ = request.args.get("format", None)

	num_get_requests = 0

	speaker_firstname_raw = request.args.get("firstname", "")
	speaker = request.args.get("surname", "")

	speaker_surname = speaker.upper()
	try:
		speaker_firstname = first_name_format(speaker_firstname_raw)
		print(speaker_firstname)
	except:
		speaker_firstname = speaker_firstname_raw

	district_query = request.args.get("district", "")
	state_query = request.args.get("state", "")
	party_query = request.args.get("party", "")
	type_query = request.args.get("type", "")

	month = request.args.get("month", "")
	month = month_dict[month] if month else ""

	day = request.args.get("day", "")
	year = request.args.get("year", "")

	connection = sqlite3.connect("mydatabase.sqlite")
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()

	all_records_query = "SELECT first_name, last_name, party, type, state, chamber, district, \
						proceeding_title, word_count, year, month, day, speech_text FROM allspeakers \
						inner join allspeeches on allspeeches.speaker_id = allspeakers.speaker_id \
						%s %s;"

	records_count = 0
	unselected_queries = []
	records_total = []
	where_clause = ""
	where_array = []
	condition_tuple = []
	if speaker_surname or speaker_firstname or district_query or state_query or party_query or type_query or month or day or year:
		where_clause += "where "
		if speaker_surname:
			where_array.append("last_name like ? ")
			condition_tuple.append(str(speaker_surname))
		else:
			unselected_queries.append('Surname')
		if speaker_firstname:
			where_array.append("first_name like ? ")
			condition_tuple.append("%" + speaker_firstname_raw + "%")
		else:
			unselected_queries.append('First Name')
		if type_query:
			where_array.append("type = ? ")
			condition_tuple.append(str(type_query))
		else:
			unselected_queries.append('Rep Type')
		if party_query:
			where_array.append("party = ? ")
			condition_tuple.append(str(party_query))
		else:
			unselected_queries.append('Party')
		if state_query:
			where_array.append("state = ? ")
			condition_tuple.append(str(state_query))
		else:
			unselected_queries.append('State')
		if district_query:
			where_array.append("district = ? ")
			condition_tuple.append(str(district_query))
		else:
			unselected_queries.append('District')
		if day:
			where_array.append("day = ? ")
			condition_tuple.append(str(day))
		else:
			unselected_queries.append('Day')
		if month:
			where_array.append("month = ? ")
			condition_tuple.append(str(month))
		else:
			unselected_queries.append('Month')
		if year:
			where_array.append("year = ? " if len(year) > 2 else "")
			condition_tuple.append(str(year))
		else:
			unselected_queries.append('Year')


		where_clause += "and ".join(where_array)
		condition_tuple = tuple(condition_tuple)

		if format_ == "csv":
			all_records_query = all_records_query % (where_clause, "ORDER BY year DESC, month DESC, day DESC LIMIT 500")
			cursor.execute(all_records_query, condition_tuple)
			records_total = cursor.fetchall()
			#flash('Downloading the first 500 records of your query! Stay tuned for the full release of searchlight, where subscribing user can download all records.')
			return download_csv(records_total, "speeches_%s.csv" % (speaker_surname.lower()))
		else:
			# count Sql query to find number of records
			count_records_query = "SELECT COUNT(first_name)" + all_records_query[134:]
			count_cond_query = count_records_query % (where_clause, "")
			cursor.execute(count_cond_query, condition_tuple)
			records_count = cursor.fetchall()[0]['COUNT(first_name)']

			#limited query statement to show users preview of records
			limit_statement = "ORDER BY year DESC, month DESC, day DESC LIMIT 30"
			all_records_query = all_records_query % (where_clause, limit_statement)
			cursor.execute(all_records_query, condition_tuple)
			records_total = cursor.fetchall()
	else:
		unselected_queries = ['Surname', 'First Name', 'Rep Type', 'Party', 'State', 'Day', 'Month', 'Year', 'District']

	years = [x for x in range(2018, 1993, -1)]
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	days = [x for x in range(1, 32)]
	parties = ['R', 'D', 'I']
	states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
	"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
	"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
	"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
	"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
	districts = [x for x in range(1, 54)]
	types = ['SENATOR', 'REPRESENTATIVE', 'DELEGATE']

	def name_format(name):
		first_char = name[0]
		rest_name = name[1:]
		return first_char.upper() + rest_name.lower()

	selected_dict = {}
	selected_dict["year"] = int(year) if year else None
	selected_dict["month"] = month if month else None
	selected_dict["day"] = int(day) if day else None
	selected_dict["state"] = state_query if state_query else None
	selected_dict["party"] = party_query if party_query else None
	selected_dict["type"] = type_query if type_query else None
	selected_dict["district"] = int(district_query) if district_query else None

	return flask.render_template('speaker.html', records=records_total, no_of_records=records_count,
		speaker_firstname=speaker_firstname_raw, speaker_surname=speaker, name_format=name_format,
		years=years, months=months, days=days, states=states, parties=parties, districts=districts,
		types=types, selected_dict = selected_dict, date_format=date_format, unselected_queries=", ".join(unselected_queries))

########################################################################
# The following are helper functions. They do not have a @app.route decorator
########################################################################
def dictionary_factory(cursor, row):
	"""
	This function converts what we get back from the database to a dictionary
	"""
	d = {}
	for index, col in enumerate(cursor.description):
		d[col[0]] = row[index]
	return d

def download_csv(data, filename):
	"""
	Pass into this function, the data dictionary and the name of the file and it will create the csv file and send it to the view
	"""
	header = data[0].keys() #Data must have at least one record.
	with open('downloads/' + filename, "w+") as f:
		writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for row in data:
			writer.writerow(list(row.values()))

	#Push the file to the view
	return send_file('downloads/' + filename,
				 mimetype='text/csv',
				 attachment_filename=filename,
				 as_attachment=True)

def first_name_format(name):
	first_char = name[0]
	rest_name = name[1:]
	return first_char.upper() + rest_name.lower()
# function to make first name Rubio

def date_format(month, day, year):
	# month_dict = {'January' : '1', 'February' : '2', 'March': '3', 'April': '4', 'May': '5', 'June': '6', 'July': '7', 'August': '8', 'September': '9', 'October': '10', 'November': '11', 'December': '12'}
	# month_str = month_dict[month]
	return str(month) + '/' + str(day) + '/' + str(year)
if __name__ == '__main__':
	app.debug=True
	app.run()
