
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
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

def get_locations():
  conn = engine.connect()
    
  # Fetch distinct school names
  cursor = conn.execute(text("SELECT DISTINCT school_name FROM school"))
  schools = [school[0] for school in cursor]

  # Fetch distinct dining hall names
  cursor = conn.execute(text("SELECT DISTINCT dining_hall_name FROM dining_hall"))
  dining_halls = [hall[0] for hall in cursor]

  # Fetch distinct cafe names
  cursor = conn.execute(text("SELECT DISTINCT cafe_name FROM cafes"))
  cafes = [cafe[0] for cafe in cursor]

  # Fetch distinct food cart names
  cursor = conn.execute(text("SELECT DISTINCT foodcart_name FROM food_cart"))
  food_carts = [food_cart[0] for food_cart in cursor]

  # Close the connection
  conn.close()

  # Combine all the lists
  locations = schools + dining_halls + cafes + food_carts
  return locations






# The string needs to be wrapped around text()

conn.execute(text("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);"""))
conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

conn.commit() 

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
@app.route('/')
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
  cursor = g.conn.execute(text("SELECT name FROM test"))
  g.conn.commit()
  #SELECT dietary_restriction FROM dining_halls WHERE dietary restriction = user input 

  # 2 ways to get results

  # Indexing result by column number
  names = [result[0] for result in cursor]
  cursor.close()

  # Get the list of schools and their corresponding sids
  locations = get_locations()

  # Get the selected school and its associated dietary need
  selected_location = request.args.get('selected_location')
  print(selected_location)

  result = []

  
  if selected_location:
    location_name = selected_location
    conn = engine.connect()

    # Check if the location exists in each table
    check_school_query = "SELECT 1 FROM school WHERE school_name = :location_name LIMIT 1"
    check_cafe_query = "SELECT 1 FROM cafes WHERE cafe_name = :location_name LIMIT 1"
    check_dining_hall_query = "SELECT 1 FROM dining_hall WHERE dining_hall_name = :location_name LIMIT 1"
    check_food_cart_query = "SELECT 1 FROM food_cart WHERE foodcart_name = :location_name LIMIT 1"

    # Determine the type of location
    if conn.execute(text(check_school_query), {"location_name": location_name}).fetchone():
      location_type = 'school'
    elif conn.execute(text(check_cafe_query), {"location_name": location_name}).fetchone():
      location_type = 'cafe'
    elif conn.execute(text(check_dining_hall_query), {"location_name": location_name}).fetchone():
      location_type = 'dining_hall'
    elif conn.execute(text(check_food_cart_query), {"location_name": location_name}).fetchone():
      location_type = 'food_cart'
    else:
      location_type = None

      # Construct the query based on the location type
    if location_type:
      if location_type.lower() == 'school':
        query = """
            SELECT r.rid, r.opinion, r.stars, r.meal_type
            FROM school s
            JOIN places_to_eat p ON s.sid = p.sid
            JOIN ref_p rp ON p.pid = rp.pid
            JOIN review r ON rp.rid = r.rid
            WHERE s.school_name = :location_name
        """
      elif location_type.lower() == 'cafe':
        query = """
            SELECT r.rid, r.opinion, r.stars, r.meal_type
            FROM cafes c
            JOIN places_to_eat p ON c.pid = p.pid
            JOIN ref_p rp ON p.pid = rp.pid
            JOIN review r ON rp.rid = r.rid
            WHERE c.cafe_name = :location_name
        """
      elif location_type.lower() == 'dining_hall':
        query = """
            SELECT r.rid, r.opinion, r.stars, r.meal_type
            FROM dining_hall d
            JOIN places_to_eat p ON d.pid = p.pid
            JOIN ref_p rp ON p.pid = rp.pid
            JOIN review r ON rp.rid = r.rid
            WHERE d.dining_hall_name = :location_name
        """
      elif location_type.lower() == 'food_cart':
        query = """
            SELECT r.rid, r.opinion, r.stars, r.meal_type
            FROM food_cart f
            JOIN ref_f rf ON f.fid = rf.fid
            JOIN review r ON rf.rid = r.rid
            WHERE f.foodcart_name = :location_name
        """

      cursor = conn.execute(text(query), {"location_name": location_name})
      result = cursor.fetchall()

      conn.close()

      print(result)
    else:
      print("Invalid location:", selected_location)
  else:
    print("Invalid selected_location:", selected_location)




  # if selected_school:
  #   school_name = selected_school.split(':')[0]  # Assuming the sid is part of the value
  #   print(school_name)
  #   conn = engine.connect()
  #   #fix and add JOIN Query 
  #   cursor = conn.execute("SELECT sid FROM school WHERE sid=?", (sid,))
  #   result = cursor.fetchone()
  #   conn.close()
  #   print(result[0])
  #   dietary_need = result[0] if result else None



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
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = {
    'data': names,
    'locations': locations,
    'selected_location': selected_location,
    'reviews': result
  }


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add(): 
  name = request.form['name']
  params_dict = {"name":name}
  g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
  g.conn.commit()
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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
