PostgreSQL Account Information

The PostgreSQL account for the database on the server resides under the following credentials:

Username: mzn2002
Password: 143318
Database: proj1part2
Host: 34.74.171.121

The web application is accessible at the following URL: http://127.0.0.1:8111

Parts Implemented from the Original Proposal (Part 1)
Database Schema and Tables: Implemented the proposed database schema with tables such as school, dining_hall, cafes, food_cart, web_feedback_suggests, visits, goes_to, places_to_eat, ref_p, ref_f, review, our_user, and review_leaves.

Web Server and Routes: Created a Flask web server with routes for the home page, search functionality, review functionality, creating a web feedback functionality,
going to the review page, and going to the web feedback page.

Database Interaction: Implemented database interactions for retrieving and displaying reviews based on selected locations. Updated the database during the creation of new reviews and during the creation of website feedback.

Parts Not Implemented from the Original Proposal (Part 1)
All parts of the original proposal were implemented as planned.

New Features Added:
We enhanced the aesthetic of the website for better user functionality. 

Non-Implemented Parts and Reasons
All proposed parts were implemented.

Interesting Web Pages and Database Operations

Home Page:
Purpose: Displays a list of names from the test table and provides a dropdown menu to select a location (school, dining hall, cafe, or food cart).
Database Operations: Retrieves names from the test table and reviews based on the selected location from various tables.
Why Interesting: This page demonstrates the integration of multiple database tables featuring different dining and food cart locations around campus, and showcases dynamic content based on user interactions.

Search Results Page:
Purpose: Allows users to search for reviews based on a location name.
Database Operations: Retrieves reviews for the searched location from various tables.
Why Interesting: This page highlights the flexibility of the application by providing a search feature that dynamically retrieves relevant reviews from different tables.

Database Schema
The web server interacts with a PostgreSQL database and includes tables such as school, dining_hall, cafes, food_cart, places_to_eat, ref_p, ref_f, and review. The schema and initial data are defined in the server code.

Routes
/ (Home): Displays a list of names from the test table and provides a dropdown menu to select a location (school, dining hall, cafe, or food cart). Reviews for the selected location are displayed.
/search: Allows users to search for reviews based on a location name. Results are displayed on the search_results.html page.
/add_review (POST): Adds a new review entry and updates all related tables based on the information submitted for ‘Write a Review’ on another.html.
/add_feedback (POST): Adds a new feedback entry and updates all related tables based on the information submitted for ‘Leave a Feedback’ on feedback.html.
/create_revpg: A route that takes you to another.html.
/create_feedbackpg: A route that takes you to feedback.html.

We used ChatGPT to debug complex errors after our TA recommended it to us to pinpoint what was wrong. Also used ChatGPT for guidance on creating the Front-end portion only. The project does strictly adhere to the project policies on the usage of AI tools.
