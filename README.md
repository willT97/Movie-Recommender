# Movie-Recommender
Web application using Flask to review and get movie recommendations

# How to use
firstly to download all of the required packages enter the flaskr directory and type the command.

pip install -r requirements.txt

To run the flask application run the commands in the terminal for Linux and Mac:
export FLASK_APP=__init__.py
export FLASK_ENV=development
flask run
For Windows cmd, user set instead of export
set FLASK_APP=__init__.py
set FlASK_ENV=development
flask run

Then go to the URL http://127.0.0.1:5000/ to load the website.

To log in to a user each users username is 'user' + the userid and the password is 'pass' + the pass id for example the user with an id = '1' the username would be 'user1' and password would be 'pass1'.

###############################################################################
Features implemented
Login and register new accounts, stores the passwords hashed and with custom salts.
Before logging in or registering, user can browse all of the movies.
Once logged in a user can rate more movies, edit or deleted movies from there rated list and see what movies they are recommended based on the movies they have seen already. Click to rate and refresh the page and it moves to the rated section.
Provides a personalised message at the top including the username of the user
Pagination to move between the pages so they are not all loaded at once.
Used the movie database api to display the movie posters for each of the films.
Provides 3 languages to choose from for the website: English, Japanese and Spanish using i18n capability.
Used a sqlite database to store the users and the ratings, I did this because of the easy access to the data through SQL queries.
Implemented low-rank matrix factorization via singular value decomposition for the movie recommendations. From the movie recommendations page the user can then review films and they will end up in the rated section.
###############################################################################
