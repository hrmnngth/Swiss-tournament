# Swiss Tournament Application

Swiss Tournament Application implements the Swiss tournament system supporting multi-players and multi-tournaments. This app implements a database schema to store game matches between players, standings, players info.

## Table of contents

* [Quick start](#quick-start)
* [Motivation](#motivation)
* [Documentation](#documentation)
* [Contributors](#contributors)
* [License](#license)


## Quick start

The steps to quick start are:

* [Download the zip file in your directory](https://github.com/hrmnngth/Swiss-tournament/archive/master.zip).
* or Clone the repo: `git clone https://github.com/hrmnngth/Swiss-tournament.git`.

#### Running the app

1. This project works with vagrant machine that includes the follow components. Make sure you have installed vagrant properly at the same level of 'repo folder'
	- python2.7
	- PostgresSQL
2. In command line connect to vagrant machine
	- ``vagrant up`` to start the virtual machine
	- ``vagrant ssh`` to log in
3. Go to the project folder:
	- ``cd /vagrant/Swiss-tournament``
5. Create the database
	sudo -u postgres psql -c "CREATE DATABASE TOURNAMENT"
6. Create tables, views, triggers. Run these in command prompt:
	- ``psql tournament`` to connect database in console
	- ``\i tournament.sql`` Implement database schema creation
7. From the root `/Swiss-tournament` directory, run `python tournament_test.py` in the command line

#### To verify code:
- Look at ```tournament.sql`` to check SQL database setup
- Look at ```tournament.py`` to check implementation of the Swiss-pairing tournament
- Look at ```tournament_test.py`` to tests the implementation. 

#### Running extended implementation
- In way to test multi-players and multi-tournaments of this implementation, use the method testTournamentMultiPlayers() inside tournament_test.py to run with many competitors and run again to test new tournament.


## Motivation

This project is the first creation of the Nanodegree program, with aim of improving skills of full stack development.


## Contributors

This project is created by [Hermann Hernández](https://twitter.com/hrmnn_mx)


## License

Code released under [the MIT license](https://github.com/twbs/bootstrap/blob/master/LICENSE).