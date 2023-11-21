
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import string 
import secrets
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://mzn2002:143318@34.74.171.121/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# To make the queries run, we need to add this commit line
#conn.commit() 

@app.before_request 
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/', methods=['GET']) #added GET to display all reviews 
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)
  #
  # example of a database query 
  #
  #cursor = g.conn.execute(text("SELECT name FROM test"))
  #g.conn.commit()

  #trying to display all the reviews and their attributes 
  #result = engine.execute("SELECT * FROM review")
  #reviews = result.fetchall() #returns all tuples

  cursor = g.conn.execute(text("SELECT opinion, stars, meal_type FROM review")) #JOIN 
  g.conn.commit()
  
  # Fetchs all results as a list of lists
  all_reviews = [list(result) for result in cursor.fetchall()]

  # Don't forget to close the cursor
  cursor.close()

  return render_template('index.html', all_reviews=all_reviews)


  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  #return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names



@app.route('/create_revpg', methods=['GET'])
def create_revpg():
  return render_template('another.html')


#attempting to create route function to handle making reviews with POST request
@app.route('/add_review', methods=['POST']) #POST for form, POST for reviews when user chooses to add data
def add_review(): 

  conn = engine.connect()

  name = request.form.get('name') #attribute of our_user data
  uni = request.form.get('uni')   #attribute of our_user data

  #retrieving the user's id based on name and uni info they input
  cursor = conn.execute(text("SELECT uid FROM our_user WHERE uni = :uni AND name = :name"), {'uni' : uni, 'name' : name})
  uid = cursor.fetchone()

  #if user does NOT exist, add them 
  if uid:
    uid = uid[0]
  else:
    #here we insert a user into our_user table & let the database generate the uid
    uid = secrets.token_hex(5) 
    cursor = conn.execute(text("INSERT INTO our_user (uid, uni, name) VALUES (:uid, :uni, :name)"), { 'uid' : uid,'uni' : uni, 'name' : name})
    conn.commit()
    
  place = request.form.get('place')
  #figuring out if the review is for a cafe, dining hall, or food cart --> when matched storing of place

  #defines dictionary with keys being table names & values being the corresponding name attribute 
  name_attribute_map = {
    "dining_hall" : "dining_hall_name",
    "cafes" : "cafe_name",
    "food_cart" : "foodcart_name",
  }

  table_foundin = None
  id_found = None

  pid = None
  fid = None
  #iterating thru ea table to check
  for table, name_attribute in name_attribute_map.items():
    find = text(f"SELECT * FROM {table} WHERE {name_attribute} = :place")
    cursor = conn.execute(find, {'place' : place })

    result = cursor.fetchone()

    if result:
      table_foundin = table #storing the table title found in
      id_found = result[0]  #storing the id of the matched query
      break #loop stops after first match

  #check which table the match was found in &
  #then set a var with the same id attribute name as in table to id_found
  if table_foundin == "dining_hall" or table_foundin == "cafes":
    pid = id_found
  elif table_foundin == "food_cart":
    fid = id_found


  #attributes data provided by the user
  meal_type = request.form.get('meal_type')
  stars = int(request.form.get('stars'))
  opinion = request.form.get('opinion')
  rev_id = secrets.token_hex(5) #since ea byte is represented by 2 characters in hexdecimal, only need 5 bytes for 10-char string


  #INSERTING REVIEW into the review table
  cursor = conn.execute(text("INSERT INTO review (rid, opinion, stars, meal_type) VALUES (:rev_id, :opinion, :stars, :meal_type)"), { 'rev_id' : rev_id,'opinion' : opinion, 'stars' : stars, 'meal_type' : meal_type})

  #liniking review to places_to_eat
  cursor = conn.execute(text("INSERT INTO ref_p (rid, pid) VALUES (:rev_id, :pid)"), {'rev_id' : rev_id, 'pid' : pid})
  
  #linking review to food_cart 
  cursor = conn.execute(text("INSERT INTO ref_f (rid, fid) VALUES (:rev_id, :fid)"), {'rev_id' : rev_id, 'fid' : fid})

  #linking review to the user
  cursor = conn.execute(text("INSERT INTO review_leaves (rid, uid) VALUES (:rev_id, :uid)"), {'rev_id' : rev_id, 'uid' : uid})

  conn.commit()


  #DISPLAYING Created Review --> displays ALL reviews created by user --> as a List
  user_reviews = conn.execute(text("SELECT opinion, stars, meal_type FROM review WHERE rid = :rev_id"), {'rev_id' :rev_id}).fetchall()

  user_reviews = [list(user_rev) for user_rev in user_reviews]

  conn.close()

  return render_template('another.html', user_reviews=user_reviews) 


#@app.route('/login')
#def login():
  #abort(401)
  #this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()



