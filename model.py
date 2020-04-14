from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
	# attributes
	customer_id = db.Column(db.Integer, primary_key=True)
	customer_name = db.Column(db.String(24), nullable=False)
	email = db.Column(db.String(80), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)
	#relationship with events
	events = db.relationship('Event', backref='scheduler')

	def __init__(self, username, email, pw_hash):
		self.customer_name = username
		self.email = email
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<Customer {}>'.format(self.customer_name)

class Staff(db.Model):
	# attributes
	staff_id = db.Column(db.Integer, primary_key=True)
	staff_name = db.Column(db.String(24), nullable=False)
	email = db.Column(db.String(80), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)
	#relationship with events
	events1 = db.relationship('Event', backref='staff1', foreign_keys = 'Event.staff1_id')
	events2 = db.relationship('Event', backref='staff2', foreign_keys = 'Event.staff2_id')
	events3 = db.relationship('Event', backref='staff3', foreign_keys = 'Event.staff3_id')

	def __init__(self, username, email, pw_hash):
		self.staff_name = username
		self.email = email
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<Staff {}>'.format(self.staff_name)

class Event(db.Model):
	#attributes
	event_id = db.Column(db.Integer, primary_key = True)
	event_name = db.Column(db.String(24), nullable=False)
	event_date = db.Column(db.String(20), nullable = False)
	event_venue = db.Column(db.String(24), nullable=False)
	staff_num = db.Column(db.Integer, nullable = False)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
	staff1_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)
	staff2_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)
	staff3_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)

	def __init__(self, name, date, venue, scheduler_id):
		self.event_name = name
		self.event_date = date
		self.event_venue = venue
		self.customer_id = scheduler_id
		self.staff1_id = None
		self.staff2_id = None
		self.staff3_id = None
		self.staff_num = 0
		
		
	def add_staff(self, staff):
                if self.staff1_id is None:
                        self.staff1_id = staff.staff_id
                        return 1
                elif self.staff2_id is None:
                        self.staff2_id = staff.staff_id
                        return 2
                elif self.staff3_id is None:
                        self.staff3_id = staff.staff_id
                        return 3
                else:
                        return 0

	def __repr__(self):
		return '<Event {}>'.format(self.event_name)
	

