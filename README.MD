# Swiss Tournament Application

Swiss Tournament Application implements the Swiss tournament system supporting multi-players and multi-tournaments. This app implements a database schema to store game matches between players, standings, players info.

## Table of contents

* [Requeriments](#requeriments)
* [Quick start](#quick-start)
* [Documentation](#documentation)
* [Contributors](#contributors)
* [License](#license)

## Requeriments

1. This project works with vagrant machine that includes the follow components. Make sure you have installed vagrant properly at the same level of 'repo folder'
	- python2.7
	- PostgresSQL
2.- Install the follow components in vagrant machine
	- psycopg2: ``sudo apt-get install python-psycopg2`` Postgres database library 
	- [names](https://pypi.python.org/pypi/names): Package index to generate random names 

sudo apt-get install python-names

## Quick start

The steps to quick start are:

* [Download the zip file in your directory](https://github.com/hrmnngth/Swiss-tournament/archive/master.zip).
* or Clone the repo: `git clone https://github.com/hrmnngth/Swiss-tournament.git`.
* check out the [Requeriments](#requeriments) to run the app

#### Running the app

1. In command line connect to vagrant machine
	- ``vagrant up`` to start the virtual machine
	- ``vagrant ssh`` to log in
2. Go to the project folder:
	- ``cd /vagrant/Swiss-tournament``
3. Create the database:
	``sudo -u postgres psql -c "CREATE DATABASE TOURNAMENT"``
4. Create tables, views, triggers. Run these in command prompt:
	- ``psql tournament`` to connect database in console
	- ``\i tournament.sql`` Implement database schema creation
5. run `python tournament_test.py` in the command line

#### To verify code:
- Look at ``tournament.sql`` to check SQL database setup
- Look at ``tournament.py`` to check implementation of the Swiss-pairing tournament
- Look at ``tournament_test.py`` to tests the implementation. 

#### Running extended implementation
- In way to test multi-players and multi-tournaments of this implementation, use the method ``testTournamentMultiPlayers()`` inside the main of ``tournament_test.py`` to run with many competitors and run again to test new tournament.

## Documentation

To see all database information (schema, tables, relation, etc) and the components, modules implemented, check [DOCUMENTATION.MD](#DOCUMENTATION.md)


## Contributors

This project is created by [Hermann Hernández](https://twitter.com/hrmnn_mx)
#### Modules used in this project
Package [names](https://pypi.python.org/pypi/names) is created by Trey Hunner, version 0.3.0, MIT License

## License

Code released under [the MIT license](https://github.com/hrmnngth/Swiss-tournament/blob/master/LICENSE).

