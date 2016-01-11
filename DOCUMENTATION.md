## Database schema:
### Tables:
- Table "public.players"
```
--------------------+---------+-----------
 player_id          | integer | not null
 full_name          | text    | 
 birthdate          | date    | 
 age                | integer | 
 register_date      | date    | 
 last_trnmnt_rgstrd | integer | 
Indexes:
    "players_pkey" PRIMARY KEY, btree (player_id)
    "players_idx01" btree (player_id)
    "players_idx02" btree (full_name)
Triggers:
    playertournament AFTER INSERT OR UPDATE ON players FOR EACH ROW EXECUTE PROCEDURE regplayertournament()
```
- Table "public.player_standings"
```
    Column     |  Type   | Modifiers 
---------------+---------+-----------
 player_id     | integer | 
 wins          | integer | 
 losses        | integer | 
 tieds         | integer | 
 matches       | integer | 
 byes          | integer | 
 tournament_id | integer | 
 Indexes:
    "player_standings_pkey" PRIMARY KEY, btree (player_id, tournament_id)
```
- Table "public.matches"
```
    Column     |            Type             | Modifiers 
---------------+-----------------------------+-----------
 tournament_id | integer                     | 
 round         | integer                     | 
 date_match    | timestamp without time zone | 
 winner        | integer                     | 
 loser         | integer                     | 
Indexes:
    "matches_idx01" btree (tournament_id, winner, loser)
Triggers:
    standings AFTER INSERT ON matches FOR EACH ROW EXECUTE PROCEDURE updatestandings()
```
- Table "public.tournament"
```
       Column       |  Type   | Modifiers 
--------------------+---------+-----------
 tournament_id      | integer | not null
 tournament_name    | text    | 
 tournament_place   | text    | 
 start_date         | date    | 
 end_date           | date    | 
 number_competitors | integer | 
 winner             | xml     | 
 second_place       | xml     | 
Indexes:
    "tournament_pkey" PRIMARY KEY, btree (tournament_id)
```
- Table "public.players_tournament"
```
    Column     |  Type   | Modifiers 
---------------+---------+-----------
 player_id     | integer | not null
 rank_ini      | integer | 
 rank_fin      | integer | 
 tournament_id | integer | not null
Indexes:
    "players_tournament_pkey" PRIMARY KEY, btree (player_id, tournament_id)
    "player_trnmnt_idx01" btree (tournament_id)
```
### Views:
- View "public.v_standings"
```
    Column     |       Type       | Modifiers 
---------------+------------------+-----------
 player_id     | integer          | 
 full_name     | text             | 
 wins          | integer          | 
 matches       | integer          | 
 byes          | integer          | 
 points        | double precision | 
 rank_ini      | integer          | 
 rank_fin      | integer          | 
 tournament_id | integer          | 
```

### Aditional Packages
This implementation is supported by the following packages. Click on it to see original source.

    - [psycopg2](http://initd.org/psycopg/docs): Postgres database library
    - [names](https://pypi.python.org/pypi/names): Package index to generate random names

### Reference of building this app
To build this app, it was based on information from different components, such as:
postgres, collections, lists, etc. 
```
Reference of using COALESCE (sql function)
http://www.lawebdelprogramador.com/foros/PostgreSQL/547420-Equivalencia-de-NVL-de-Oracle.html

Reference of using left outer join (sql sentence)
http://www.postgresql.org/docs/8.3/static/tutorial-join.html

Pasing parameters in python programming postgres
http://initd.org/psycopg/docs/usage.html#query-parameters
http://stackoverflow.com/questions/9075349/using-insert-with-a-postgresql-database-using-python
http://stackoverflow.com/questions/4113910/python-psycogp2-inserting-into-postgresql-help
http://initd.org/psycopg/docs/usage.html#query-parameters

Reference of using namedtuple
https://docs.python.org/2/library/collections.html#module-collections    

Reference of using random
http://stackoverflow.com/questions/976882/shuffling-a-list-of-objects-in-python
http://www.pythonforbeginners.com/random/how-to-use-the-random-module-in-python

Reference of programming python
https://docs.python.org/2/tutorial/
http://www.tutorialspoint.com/python/python_variable_types.htm
https://docs.python.org/2/library/index.html

Reference of using random names
https://pypi.python.org/pypi/names/
https://github.com/treyhunner/names

Reference of using lists
http://stackoverflow.com/questions/627435/how-to-remove-an-element-from-a-list-by-index-in-python

Reference of using itertools
https://docs.python.org/2/library/itertools.html
```









