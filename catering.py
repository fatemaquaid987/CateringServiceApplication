import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash

from model import db, Customer, Staff, Event
from datetime import datetime as dt

app = Flask(__name__)

# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')

app.config.from_object(__name__)
#app.config.from_envvar('MINITWIT_SETTINGS', silent=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning

db.init_app(app)
owner_user = "owner"
owner_pass = "pass"


@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.create_all()
	print('Initialized the database.')
	

def get_customer_id(customername):
	"""Convenience method to look up the id for a customername."""
	rv = Customer.query.filter_by(customer_name=customername).first()
	return rv.customer_id if rv else None

def get_staff_id(staffname):
	"""Convenience method to look up the id for a staffname."""
	rv = Staff.query.filter_by(staff_name=staffname).first()
	return rv.staff_id if rv else None

@app.route("/")
def default():
	return redirect(url_for("login_controller"))
	
@app.route("/login/", methods=["GET", "POST"])
def login_controller():
	# first check if the user is already logged in
	
	if "user_id" in session:
		flash("Already logged in!")
		return redirect(url_for("profile", username=session["user_name"]))

	# if not, and the incoming request is via POST try to log them in
	elif request.method == "POST":
		#customer
		customer = Customer.query.filter_by(customer_name=request.form['user']).first()
		#staff
		staff = Staff.query.filter_by(staff_name=request.form['user']).first()
		
		#if customer is in database
		if customer is not None:
			#if password matches
			if check_password_hash(customer.pw_hash, request.form['pass']):
				session["user_id"] = customer.customer_id
				session["user_name"] = customer.customer_name
				flash("Customer successfully logged in!")
				return redirect(url_for("profile", username=session["user_name"]))
			else:
				flash("Invalid password")
			
		#else if staff is in database
		elif staff is not None:
			if check_password_hash(staff.pw_hash, request.form['pass']):
				session["user_id"] = staff.staff_id
				session["user_name"] = staff.staff_name
				flash("Staff successfully logged in!")
				return redirect(url_for("profile", username = session["user_name"]))
			else:
				flash("Invalid password")
		#owner
		elif request.form["user"] == owner_user:
			if request.form["pass"] == owner_pass:
				session["user_id"] = 0
				session["user_name"] = owner_user
				flash("Owner successfully logged in!")
				return redirect(url_for("profile", username = owner_user))
			else:
			    
				flash("Invalid password")
		else:
			flash("Invalid username")

	# if all else fails, offer to log them in
	return render_template("loginPage.html")
    
@app.route("/event/")
def all_events():
	return render_template("events.html", events=Event.query.all())

@app.route("/event/<eventname>", methods = ["GET", "POST"])
def event(eventname=None):
	#event name not specified
	if not eventname:
		return redirect(url_for("all_events"))
	event = Event.query.filter_by(event_name=eventname).first()
	    
	#event name specified and in events 
	if event is not None:
		# check if method is post
		if request.method == "POST":
			if "user_id" in session:
				customer = Customer.query.filter_by(customer_name=session["user_name"]).first()
				staff = Staff.query.filter_by(staff_name=session["user_name"]).first()
				if staff is not None:
					#user in session is staff, signup staff for this event, add staff to events table
					if event.staff1_id is None:
						event.staff1_id = staff.staff_id
						event.staff_num += 1
					elif event.staff2_id is None:
						event.staff2_id = staff.staff_id
						event.staff_num +=1
					elif event.staff3_id is None:
						event.staff3_id = staff.staff_id
						event.staff_num +=1
					db.session.commit()
					flash("You successfully signed up for this event")
					return redirect(url_for("profile", username = session["user_name"]))
					
				elif customer is not None:
					#user in session is customer,cancel event, remove from events table
					Event.query.filter_by(event_id = event.event_id).delete()
					db.session.commit()
					flash("Event succesfully canceled")
					return redirect(url_for("profile", username = session["user_name"]))
		else:
			if "user_id" in session:
				customer = Customer.query.filter_by(customer_name=session["user_name"]).first()
				staff = Staff.query.filter_by(staff_name=session["user_name"]).first()
				if customer is not None:
					#user in session is customer, send cancel_button as argument
					if event.customer_id == customer.customer_id:
					
						return render_template("eventPage.html", event = event, button = "cancel")
				elif staff is not None:
					#user in session is staff, send signup button as argument
					if ((event.staff1_id is None) or (event.staff2_id is None) or (event.staff3_id is None)):
						if event.staff1_id is not staff.staff_id and event.staff2_id is not staff.staff_id and event.staff3_id is not staff.staff_id:
							return render_template("eventPage.html", event = event, button = "signup")
			
		return render_template("eventPage.html", event = event)
	else:
		# cant find eventpage
		abort(404)
		    
	    
					    
@app.route("/profile/")
def profiles():
	return render_template("profiles.html", customers=Customer.query.all(), staff = Staff.query.all(), owner = owner_user)

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username=None):
	print(username)
	if not username:
		return redirect(url_for("profiles"))
	customer = Customer.query.filter_by(customer_name=username).first()
	staff = Staff.query.filter_by(staff_name=username).first()
	
	#if customer is in database
	if customer is not None:
		# if specified, check to handle customers looking up their own profile
		if "user_id" in session:
			if session["user_name"] == username:
				e = Event.query.filter_by(customer_id = customer.customer_id).all()
				if request.method == "POST":
					if not request.form['eventname']:
						flash("Please enter an event name to register!")
						return render_template("curProfile.html", events = e)
					elif not request.form['date']:
						flash("Please enter a date to register!")
						return render_template("curProfile.html", events = e)
					elif not request.form['venue']:
						flash("Please enter a venue to register!")
						return render_template("curProfile.html", events = e)
					
					event = Event.query.filter_by(event_name=request.form["eventname"]).first()
					event_d = Event.query.filter_by(event_date=str(request.form["date"])).first()
					#check if event name already exists 
					if event is not None:
						flash("Event name already taken!")
						return render_template("curProfile.html", events = e)
					#check if event date is already taken
					elif event_d is not None:
						flash("An event is already scheduled on this date!")
						return render_template("curProfile.html", events = e)
					elif dt.strptime(str(request.form["date"]) , "%Y-%m-%d") <= dt.today():
						flash("Please enter a date after today's date!")
						return render_template("curProfile.html", events = e)
					#else add event entry into the table
					else:
						db.session.add(Event(request.form['eventname'], request.form['date'], request.form['venue'], customer.customer_id))
						db.session.commit()
						
						flash("Event successfully created")
						#redirect to the created events page
						return redirect(url_for("event", eventname = request.form["eventname"]))
				
				return render_template("curProfile.html", events=e)
		other_cust = Customer.query.filter_by(customer_name = username).first()
		other_eve = Event.query.filter_by(customer_id = other_cust.customer_id).all()
		return render_template("otherProfile.html", name = username, customer=other_cust, events = other_eve)
	#if staff
	elif staff is not None:
		# if specified, check to handle staff looking up their own profile
		if "user_id" in session:
			if session["user_name"] == username:
				
				e_signed = Event.query.filter_by(staff1_id = staff.staff_id).all()+ Event.query.filter_by(staff2_id = staff.staff_id).all() + Event.query.filter_by(staff3_id = staff.staff_id).all()
				staffs = Staff.query.all()
				e_not_signed = Event.query.filter((Event.staff_num < 3), ((Event.staff1_id == None)|(Event.staff1_id != staff.staff_id)),((Event.staff2_id == None) |(Event.staff2_id !=staff.staff_id)),((Event.staff3_id == None)|(Event.staff3_id !=staff.staff_id))).all()                            
				#e_not_signed = Event.query.all()
				return render_template("staffProfile.html", events_signed=e_signed , events_not=e_not_signed)
		other_staff = Staff.query.filter_by(staff_name = username).first()
		other_eve = Event.query.filter_by(staff1_id = other_staff.staff_id).all()+ Event.query.filter_by(staff2_id = other_staff.staff_id).all() + Event.query.filter_by(staff3_id = other_staff.staff_id).all()
		return render_template("otherProfile.html", staff = other_staff, events = other_eve)
	
	#if owner 
	elif username == owner_user:
		
		#if owner is looking for his own profile
		if "user_id" in session:
			if session["user_name"] == username:
				e = Event.query.all()
				s = Staff.query.all()
				return render_template("ownerProfile.html", name = username, events=e, staff_table = Staff )
		
		return render_template("otherProfile.html", name=username)
	else:
		# cant find profile
		abort(404)

@app.route("/logout/")
def unlogger():
	# if logged in, log out, otherwise offer to log in
	if "user_id" in session:
		# note, here were calling the .clear() method for the python dictionary builtin
		session.clear()
		# flashes are stored in session["_flashes"], so we need to clear the session /before/ we set the flash message!
		flash("Successfully logged out!")
		# we got rid of logoutpage.html!
		return redirect(url_for("login_controller"))
	else:
		flash("Not currently logged in!")
		return redirect(url_for("login_controller"))


@app.route("/customer_register/", methods=["GET", "POST"])
def c_reg():
	
	# if logged in, redirect to profile 
	if "user_id" in session:
		customer = Customer.query.filter_by(customer_name= session['user_name']).first()
		staff = Staff.query.filter_by(staff_name = session['user_name']).first()
		# is user in session is not the customer
		if customer is None:
			flash("Only customers can sign up for a new account")
			# user in session is staff, redirect them to their profile
			if staff is not None:
				return redirect(url_for("profile", username=session["user_name"]))
			#else person in session is the owner, redirect to owner profile
			else:
				return redirect(url_for("profile", username=session["user_name"]))
		#user in session is the customer, ask them to log out to sign up for a new account
		else:
			      
			flash("Must log out to sign up for a new account!")                         
			return redirect(url_for("profile", username=session["user_name"]))

	# is not logged in and method is post
	elif request.method == "POST":
	    
		customer = Customer.query.filter_by(customer_name = request.form["user"]).first()
		staff = Staff.query.filter_by(staff_name = request.form["user"]).first()
		if not request.form['user']:
			flash('You have to enter a username')
			return render_template("cusSignupPage.html")
		elif not request.form['email'] or \
				'@' not in request.form['email']:
			flash('You have to enter a valid email address')
			return render_template("cusSignupPage.html")
		elif not request.form['pass']:
			flash('You have to enter a password')
			return render_template("cusSignupPage.html")
		#if name is already in customer table
		elif customer is not None:
			flash("Username already taken!")
			return render_template("cusSignupPage.html")
		elif staff is not None:
			flash("Username already taken!")
			return render_template("cusSignupPage.html")
		elif request.form['user'] == owner_user:
			flash("Username already taken!")
			return render_template("cusSignupPage.html")
		#else add customer to the customer table
		else:
			db.session.add(Customer(request.form['user'], request.form['email'], generate_password_hash(request.form['pass'])))
			db.session.commit()
			flash('You were successfully registered and can login now')
			#session["username"] = request.form["user"]
			#flash("Successfully registered! Here is your profile")
			return redirect(url_for("login_controller"))
		    
	elif request.method == "GET":
	    return render_template("cusSignupPage.html")

	# if all else fails, offer to log them in
	
	return redirect(url_for("login_controller"))
		
@app.route("/staff_register/", methods=["GET", "POST"])
def s_reg():
	
	# if logged in, redirect to profile 
	if "user_id" in session:
		#if user in session is not the owner, redirect to profile page
		if session["user_name"] != owner_user:
			flash("Only owner is authorized to register a staff acount")
			customer = Customer.query.filter_by(customer_name= session['user_name']).first()
			staff = Staff.query.filter_by(staff_name = session['user_name']).first()
			#if person in session is staff redirect to their profile
			if staff is not None:
				return redirect(url_for("profile", username=session["user_name"]))
			    
			#else person in session is customer, redirect to their profile
			else:
				return redirect(url_for("profile", username=session["user_name"]))
		
		#if user in session is the owner, redirect to staff registration page
		elif session["user_name"] == owner_user:
			print("helloworld")
			if request.method == "POST":
				customer = Customer.query.filter_by(customer_name = request.form["user"]).first()
				staff = Staff.query.filter_by(staff_name = request.form["user"]).first()
				if not request.form['user']:
					flash('You have to enter a username')
					return render_template("staffSignupPage.html")
				elif not request.form['email'] or \
						'@' not in request.form['email']:
					flash('You have to enter a valid email address')
					return render_template("staffSignupPage.html")
				elif not request.form['pass']:
					flash('You have to enter a password')
					return render_template("staffSignupPage.html")
				#if name is already in customer or staff table
				elif customer is not None:
					flash("Username already taken!")
					return render_template("staffSignupPage.html")
				elif staff is not None:
					flash("Username already taken!")
					return render_template("staffSignupPage.html")
				elif request.form['user'] == owner_user:
					flash("Username already taken!")
					return render_template("staffSignupPage.html")
				#else add staff to the customer table
				else:
					db.session.add(Staff(request.form['user'], request.form['email'], generate_password_hash(request.form['pass'])))
					db.session.commit()
					flash('Staff successfully registered. The memeber can login now')
					return redirect(url_for("profile", username=owner_user))
			else:
				return render_template("staffSignupPage.html")

	# if all else fails, offer to log them in
	flash("If you are the owner, login to register a staff acount")
	return redirect(url_for("login_controller"))

# needed to use sessions
# note that this is a terrible secret key

app.secret_key = "this is a terrible secret key"
			
if __name__ == "__main__":
	app.run()

