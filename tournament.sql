-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

drop view if exists v_standings;
drop table if exists tournament;
drop table if exists matches;
drop table if exists players;
drop table if exists player_standings;
drop table if exists players_tournament;
drop sequence if exists id_tournament_sequence;
drop sequence if exists id_player_sequence;



create table tournament (
	tournament_id integer PRIMARY KEY, 
	Tournament_name text, 
	Tournament_place text, 
	start_date date,  
	end_date date, 
	number_competitors integer, 
	winner xml, 
	second_place xml);

create table matches ( 
	tournament_id integer, 
	round integer, 
	date_match timestamp, 
	winner integer, 
	loser integer );

create index matches_idx01 on matches (winner,loser);

create table players (
	player_id integer PRIMARY KEY,
	full_name text,
	birthdate date,
	age integer,
	register_date date,
	last_trnmnt_rgstrd integer);

create table player_standings ( 
	player_id integer, 
	wins integer, 
	losses integer, 
	tieds integer,
	matches integer,
	byes integer,
	points double precision,
	tournament_id integer );

ALTER TABLE player_standings ADD PRIMARY KEY (player_id,tournament_id);


create table players_tournament (
	player_id integer,
	rank_ini integer,
	rank_fin integer,
	tournament_id integer);
ALTER TABLE players_tournament ADD PRIMARY KEY (player_id,tournament_id);

create view v_standings as 
	SELECT A.PLAYER_ID, A.FULL_NAME, COALESCE(B.WINS,0) WINS, 
    COALESCE(B.MATCHES,0) MATCHES,b.byes, B.POINTS, a.RANK_INI,a.rank_fin, a.TOURNAMENT_ID FROM 
    (select c.player_id,c.full_name,d.rank_ini,D.RANK_FIN,d.tournament_id 
    from players c, players_tournament d where c.player_id=d.player_id) A 
    LEFT OUTER JOIN PLAYER_STANDINGS B ON 
    (A.PLAYER_ID=B.PLAYER_ID and b.tournament_id=a.tournament_id)
    ORDER BY TOURNAMENT_ID, WINS desc, byes desc, points desc,TIEDS;



create sequence id_player_sequence start 101 maxvalue 999999;
create sequence id_tournament_sequence start 10001 maxvalue 99999;

create or replace function regPlayerTournament() returns trigger as $regPlayerTournament$
	begin
		insert into players_tournament (player_id,rank_ini,rank_fin,tournament_id)
			values(new.player_id,0,0,new.last_trnmnt_rgstrd);
		return null;
	end;

$regPlayerTournament$ language plpgsql;

create trigger playerTournament
	after insert or update on players
	for each row
	execute procedure regPlayerTournament();

create or replace function updateStandings() returns trigger as $updateStandings$
	begin

		if new.loser=0 then
			update player_standings set wins=wins+1, matches=matches+1, byes=byes+1
				where player_id=new.winner and tournament_id=new.tournament_id;
			if not found then
				insert into player_standings (player_id, wins, losses, tieds, matches,byes,points, tournament_id)
					values (new.winner, 1,0,0,1,1,new.round/2,new.tournament_id);
			end if;
		end if;

		if new.loser>0 then

			update player_standings set wins=wins+1, matches=matches+1, points=points+new.round
				where player_id=new.winner and tournament_id=new.tournament_id;
			if not found then
				insert into player_standings (player_id, wins, losses, tieds, matches,byes,points, tournament_id)
					values (new.winner, 1,0,0,1,0,1,new.tournament_id);
			end if;
		
			update player_standings set losses=losses+1, matches=matches+1
				where player_id=new.loser and tournament_id=new.tournament_id;
			if not found then
			insert into player_standings (player_id, wins, losses, tieds, matches,byes,points, tournament_id)
				values (new.loser, 0,1,0,1,0,0,new.tournament_id);
			end if;
		end if;
		return null;
	end;

$updateStandings$ language plpgsql;

create trigger standings
	after insert on matches
	for each row
	execute procedure updateStandings();





