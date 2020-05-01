# Catering Service App #
A catering service application to help manage a catering company made using HTML5, CSS3, Python, FLASK, SQLAlchemy and,  
JavaScript.

## Overview
This is a website to help manage a catering company. For this website, there are three classes of users: the owner of the company, company staff, and registered customers. Customers will request events on given days (or cancel events they had previously requested), staff will sign up to work events, and the owner will give a rundown of what events are scheduled and who is working each event. The company cannot schedule more than 1 event per day, and each event needs only 3 Staff members to run.  

## How to run

Install Python 3.5, Flask, SQLAlchemy and, the Flask-SQLAlchemy extension.
On Windows open Command prompt or terminal on Mac.  
Set the FLASK_APP environment variable to your budget.py as: "set FLASK_APP=path/catering.py"  
Initialize the database using: "flask initdb"  
Run the application using: "flask run"  

## Specifications

Each user (Owner, Staff, or Customer) has a username and password.  
Customers are free to register for their own account. 
Staff accounts must be created by the Owner (it is fine for the Owner to set passwords for the Staff).  
Users will always have access to a logout link.  

### Owner
Owner can login with the username "owner" and password "pass" which is hardcoded for ease.  
Once logged in, the Owner will be presented with a link to create new staff accounts, and a list of all scheduled events.  
For each event, the Staff members signed up to work that event will be listed.  
If no events are scheduled, a message will be displayed informing the Owner of this.    
If any scheduled event has no staff signed up to work, a message will be displayed informing the Owner of this.  

### Staff
Once logged in, Staff members will be presented with a list of events they are scheduled to work and a list of events that they can sign up to work.  
For each event that a Staff member can sign up to work, they will be provided a link to sign up for that event.  
No event that already has 3 Staff members signed up to work will be presented as a sign up option for other Staff members.  

### Customers
Once logged in, Customers will be presented with a form to request a new event, and a list of events they have already requested.  
If a Customer requests an event on a date when another event is already scheduled, they will be presented with a message saying that the company is already booked for that date.  
For each requested event, the Customer will be provided with a link to cancel that event.  


All the data for this application( except owner's ) will be stored in an SQLite database named "catering.db" using SQLAlchemy's ORM and the Flask-SQLAlchemy extension.  