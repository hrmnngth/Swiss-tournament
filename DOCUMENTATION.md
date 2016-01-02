## Database scheme:
### Tables:
- Table "public.players"
```    Column       |  Type   | Modifiers 
--------------------+---------+-----------
 player_id          | integer | not null
 full_name          | text    | 
 birthdate          | date    | 
 age                | integer | 
 register_date      | date    | 
 last_trnmnt_rgstrd | integer | 
Indexes:
    "players_pkey" PRIMARY KEY, btree (player_id)
Triggers:
    playertournament AFTER INSERT OR UPDATE ON players FOR EACH ROW EXECUTE PROCEDURE regplayertournament()
```
- Table "public.player_standings"
``` Column     |  Type   | Modifiers 
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
``` Column     |            Type             | Modifiers 
---------------+-----------------------------+-----------
 tournament_id | integer                     | 
 round         | integer                     | 
 date_match    | timestamp without time zone | 
 winner        | integer                     | 
 loser         | integer                     | 
Triggers:
    standings AFTER INSERT ON matches FOR EACH ROW EXECUTE PROCEDURE updatestandings()
```
- Table "public.tournament"
```    Column       |  Type   | Modifiers 
--------------------+---------+-----------
 tournament_id      | integer | not null
 tournament_name    | text    | 
 tournament_place   | text    | 
 start_date         | date    | 
 end_date           | date    | 
 number_competitors | integer | 
 winner             | integer | 
 second_place       | integer | 
Indexes:
    "tournament_pkey" PRIMARY KEY, btree (tournament_id)
```
- Table "public.players_tournament"
``` Column     |  Type   | Modifiers 
---------------+---------+-----------
 player_id     | integer | 
 rank_ini      | integer | 
 rank_fin      | integer | 
 tournament_id | integer | 
Indexes:
    "players_tournament_pkey" PRIMARY KEY, btree (player_id, tournament_id)
```
### Views:
- View "public.v_standings"
``` Column     |  Type   | Modifiers 
---------------+---------+-----------
 player_id     | integer | 
 full_name     | text    | 
 wins          | integer | 
 matches       | integer | 
 rank_ini      | integer | 
 tournament_id | integer | 



