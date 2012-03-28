# MovieListr

A failed project that tried to be a sort of Delicious Library for your movies as a web-application.

It gathered all the movies it could from the Rotten Tomatoes Movies Directory, then looked for extensive info on every movie through the Netflix API, and presented a pretty thourouh movie library to the users, from which they could pick and choose the movies they owned, and tagged them according to where they stored them, be them physical or digital copies.  Trailers for movies were grabbed from the YouTube API.

Allowed the users to add movies to their libraries or favorites as well.

It provided some social functions such as friending, recommendations, similar movies, etc.

See it in action: [http://movielistr.davemode.com/](http://movielistr.davemode.com/)

# Requirements

* Python
* Django
* MySQL
* Netflix Python library

# Installation

Once you create the database, user and password for the app, you should be able to get up and running with a quick:

    python manage.py syncdb

For the crons to work you will have to register and get a Netflix API key and all that.  Provided with the app is a dump of the data in **db/dump/movielistr.sql** is a data dump which should get you up and running with some info.