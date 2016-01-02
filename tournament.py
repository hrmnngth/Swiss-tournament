#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import collections
import random
import player
import itertools
import datetime

class TournamentSwissDb(object):
    _connection = None
    _cursor = None
    _tournament_id = None
    _statusInit = False
    _round = 0
    _total_rounds = 0
    _competitors = 0

    def __init__(self):
        self.statusConnect = False

    def connect(self):
        '''Connect to the PostgreSQL database.Returns a database connection'''

        connection = psycopg2.connect(
            'dbname=tournament user=vagrant password=')
        self._connection = connection
        self._cursor = connection.cursor()
        self.statusConnect = True
        print ('connection to DB is open')

    def deleteMatches(self):
        '''Remove all the match records from the database.'''

        query = 'DELETE FROM MATCHES'
        self._cursor.execute(query)
        self._connection.commit()

    def deletePlayers(self):
        '''Remove all the player records from the database.'''

        query = 'DELETE FROM PLAYERS'
        self._cursor.execute(query)
        self._connection.commit()

    def countPlayers(self):
        '''Returns the number of players currently registered.

        Returns: 
          total_players: (int) the total count of players
        '''
        query = 'SELECT COUNT(1) as TOTAL_PLAYERS FROM PLAYERS'
        self._cursor.execute(query)
        rows = self._cursor.fetchone()
        return rows[0]

    def registerPlayer(self, name):
        '''Adds a player to the tournament database.

        The database assigns a unique serial id number for the player.  (This
        should be handled by your SQL database schema, not in your Python code.)
        Args:
          name: the player's full name (need not be unique).
        '''
        c = self.checkAlreadyRegistered(name)
        if c > 0:
            query = 'UPDATE PLAYERS SET LAST_TRNMNT_RGSTRD=%s \
                     WHERE PLAYER_ID=%s'
            print name
            data = (self._tournament_id, c)
            self._cursor.execute(query, data)
            self._connection.commit()
        else:
            query = '''INSERT INTO PLAYERS (PLAYER_ID, FULL_NAME, LAST_TRNMNT_RGSTRD)\
                    VALUES (nextval('id_player_sequence'),%s,%s);'''
            data = (name, self._tournament_id)
            self._cursor.execute(query, data)
            self._connection.commit()


    def checkAlreadyRegistered(self, name):
        '''Verifies if player already registered in the DB

        Args:
            name: (string) the player's full name 
        returns:
            if exists returns the id of the player otherwise 0
        '''
        query = 'SELECT PLAYER_ID FROM PLAYERS WHERE FULL_NAME=%s'
        data = (name,)
        self._cursor.execute(query, data)
        result = self._cursor.fetchone()
        if result and result[0] > 0:
            return result[0]
        return 0

    def playerStandings(self):
        '''Returns a list of the players and their win records, sorted by wins.

        The first entry in the list should be the player in first place, or a player
        tied for first place if there is currently a tie.
        Returns:
          A list of tuples, each of which contains (id, name, wins, matches):
            id: the player's unique id (assigned by the database)
            name: the player's full name (as registered)
            wins: the number of matches the player has won
            matches: the number of matches the player has played
        '''
        # Define a namedtuple collection
        player_standings = collections.namedtuple(
            'playerStandings', 'id, name, wins, matches')
        standings = []
        query = 'SELECT PLAYER_ID,FULL_NAME, WINS,MATCHES FROM V_STANDINGS'
        self._cursor.execute(query)
        # Adds the result of standings to the collection
        for rows in map(player_standings._make, self._cursor.fetchall()):
            standings.append(rows)

        return standings

    def reportMatch(self, winner, loser):
        '''Records the outcome of a single match between two players.

        Args:
          winner:  the id number of the player who won
          loser:  the id number of the player who lost
        '''
        query = 'INSERT INTO MATCHES (TOURNAMENT_ID,WINNER, LOSER)\
                 VALUES (%s,%s,%s);'
        data = (self._tournament_id, winner, loser)
        self._cursor.execute(query, data)
        self._connection.commit()

    def swissPairings(self):
        '''Returns a list of pairs of players for the next round of a match.

        Assuming that there are an even number of players registered, each player
        appears exactly once in the pairings.  Each player is paired with another
        player with an equal or nearly-equal win record, that is, a player adjacent
        to him or her in the standings.
        Returns:
          A list of tuples, each of which contains (id1, name1, id2, name2)
            id1--> the first player's unique id
            name1--> the first player's name
            id2--> the second player's unique id
            name2: the second player's name
        '''
        pairings = []
        y, z = 0, 1
        query = 'SELECT PLAYER_ID, FULL_NAME FROM V_STANDINGS'
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        # create the pairs of players into a list based on the standings
        for x in range(len(rows)//2):
            pairings.append((rows[y][0], rows[y][1], rows[z][0], rows[z][1]))
            y += 2
            z += 2

        return pairings

    def swissPairingsExtend(self):
        '''Returns a list of pairs of players for the next round of a match.
           It supports multip-players and multi-tournaments

        Assuming that there are an even number of players registered, each player
        appears exactly once in the pairings.  Each player is paired with another
        player with an equal or nearly-equal win record, that is, a player adjacent
        to him or her in the standings. If a player got a round bye, in the next round
        it has the hightest priority to make the first match 

        Returns:
          A list of tuples, each of which contains (id1, name1, id2, name2)
            id1: the first player's unique id
            name1: the first player's name
            id2: the second player's unique id
            name2: the second player's name
        '''
        pairings = list()
        prev_last_player = None
        bck_last_player = list()
        query = 'SELECT WINS, PLAYER_ID, FULL_NAME FROM V_STANDINGS WHERE \
                 TOURNAMENT_ID=%s'
        data = (self._tournament_id,)
        self._cursor.execute(query, data)
        rows = self._cursor.fetchall()
        # Convert the list (rows) into dictionary and create the pairs for the
        # next round randomly; it takes WINS as key. If there are an odd number,
        # assigns the last player of dictionary to a round bye.
        # Make match with priority (player-round_bye), avoids to pair players again
        v_stndgs = collections.defaultdict(list)
        for w, p, n in rows:
            # win-->key,(player object)-->item-info
            v_stndgs[w].append(player.Player(w, p, n))
        max_len_stnds = len(v_stndgs)
        count_keys = 1
        print '--- Standings (id,name,wins) ---'         
        for k in v_stndgs.iterkeys():            
            for w in v_stndgs[k]:
                print w.getPlayerId(), '|', w.getName()[:10],'|',w.getWins()
            pairings_tmp = list()
            alrdy_match = True
            bck_items = [m for m in v_stndgs[k]]
            # work on each items group (list) based on standings, 
            # from lowest to hightest
            while v_stndgs[k]:
                tot_items = len(v_stndgs[k])
                # always starting with the first player of the list
                actual_player = v_stndgs[k][0]
                # last player of the dict
                if (tot_items == 1 and count_keys == max_len_stnds):
                    if not prev_last_player:
                        # If there's not a last player of the previous key, it
                        # gets a round bye
                        self.roundBye(actual_player, self._round)
                    else:
                        # make pairing last player of previous key with the
                        # last one of dict
                        val_rndm = 0
                        pairings_tmp.append((prev_last_player.getPlayerId(),
                                        prev_last_player.getName(),
                                        v_stndgs[k][val_rndm].getPlayerId(),
                                        v_stndgs[k][val_rndm].getName()))
                        del v_stndgs[k][val_rndm]
                        prev_last_player = []
                        break
                if tot_items == 1:  # last player of the list
                    prev_last_player = actual_player
                    break
                if not prev_last_player:
                    cnt = 0
                    # get the opponent based on priority, first all player with previous bye
                    # the result is the position in the current list
                    oppnt_player = self.getPlayerBye(v_stndgs[k][1:])
                    if oppnt_player == -1:
                        val_rndm = random.randint(1, tot_items-1)
                    else:
                        val_rndm = oppnt_player
                    while alrdy_match:
                        # check if the opponents have already matched in order to
                        # get a new opponent randonmly
                        alrdy_match = self.previusMatch(
                            actual_player.getPlayerId(),
                            v_stndgs[k][val_rndm].getPlayerId())
                        if alrdy_match == True and cnt >= tot_items:
                            # this condition allows to shuffle the whole list, 
                            # it's a scenario to break an infinity loop
                            random.shuffle(bck_items)
                            v_stndgs[k] = [m for m in bck_items]
                            if v_stndgs[k-1]:
                                prev_last_player = v_stndgs[k-1][0]
                            else:
                                prev_last_player = None
                            pairings_tmp = []
                            break
                        if alrdy_match == True:
                            val_rndm = random.randint(1, tot_items-1)
                        cnt += 1
                    else:
                        alrdy_match = True
                        pairings_tmp.append((actual_player.getPlayerId(),
                                        actual_player.getName(),
                                        v_stndgs[k][val_rndm].getPlayerId(),
                                        v_stndgs[k][val_rndm].getName()))
                        # delete the opponents of the list after they got
                        # paired
                        del v_stndgs[k][val_rndm]
                        del v_stndgs[k][0]
                else:
                    # This block make pairing between last player of previous
                    # key and the current player
                    val_rndm = 0
                    while alrdy_match:
                        alrdy_match = self.previusMatch(
                            prev_last_player.getPlayerId(), 
                            v_stndgs[k][val_rndm].getPlayerId())
                        if alrdy_match == True:
                            val_rndm = random.randint(1, tot_items-1)
                    else:
                        alrdy_match = True
                        pairings_tmp.append(
                            (prev_last_player.getPlayerId(), 
                            prev_last_player.getName(), 
                            v_stndgs[k][val_rndm].getPlayerId(), 
                            v_stndgs[k][val_rndm].getName()))
                        del v_stndgs[k][val_rndm]
                        prev_last_player = None
            count_keys += 1
            pairings.extend(pairings_tmp)   
        self._round += 1

        return pairings

    def roundBye(self, player, round_):
        ''' Sets up a player-round-bye when there are an odd number of competitors

        When the number of competitors is not an even number, according to 
        Swiss-Style Pairing rules it establishes after pairings are completed
        the player remaining receives a bye, equaling one match win.

        Args:
          id_player: (int) the player's unique id
          round_: (int) the round's id
        '''
        current_date = datetime.datetime.now()
        current_date= current_date.replace(microsecond=0)
        query = 'INSERT INTO MATCHES (TOURNAMENT_ID, ROUND, DATE_MATCH, WINNER, LOSER) \
            VALUES (%s,%s,%s,%s,%s);'
        data = (self._tournament_id, round_, current_date, player.getPlayerId(), 0)
        self._cursor.execute(query, data)
        self._connection.commit()

    def previusMatch(self, player1, player2):
        '''Verify if the opponents have already match

        This function allows to check the proposal match between players
        and avoid to match each other again. Alwasy it'll be a single match.
        Args:
          player1: (int) the id_player of first opponent
          player2: (int) the id_player of second opponent
        Returns:
          True in case if already exists a previous match
          False otherwise
        '''
        matchedBoolean = False
        query = 'SELECT count(1)tot FROM MATCHES where WINNER IN(%s,%s) \
                and loser in(%s,%s) AND TOURNAMENT_ID=%s'
        data = (player1, player2, player1, player2, self._tournament_id)        
        self._cursor.execute(query, data)
        result = self._cursor.fetchone()
        if int(result[0]) > 0:
            matchedBoolean = True
        return matchedBoolean

    def getPlayerBye(self, list_):
        '''Verify if there's a player who had a round bye to be paired

        In order to make pairings, the hightest priority are the players who
        had taken a round bye.
        Args:
          list_: (list) It is the list which contain the players with the same standing
        Returns:
          Index_list: (int) The index in the list if found a player-bye
        '''
        index_list = -1
        query = 'SELECT PLAYER_ID FROM PLAYER_STANDINGS where BYES>0 and \
                TOURNAMENT_ID=%s'
        data = (self._tournament_id,)
        self._cursor.execute(query, data)
        result = self._cursor.fetchall()
        # print list_
        for iter1 in result:
            idx = 1
            for iter2 in list_:
                if iter1[0] == iter2.getPlayerId():
                    index_list = idx
                    break
            idx += 1
        return index_list

    def setTournamentInfo(self, settings):
        ''' Define an id for the tournament, in order to support multi-tournaments

        The information is store in the database and it has relation with players,
        matches and the standings, in order to support multi-tournaments with 
        the players already registered. At the beggining the winner and second place
        are not defined.

        Args:
          data: (list) an structure of values for setting the tournament 
                [id,tournament's name, tournament's place, date_start, date_end, 
                number of competitors, winner (None), second place (None)]
        '''
        self._tournament_id = settings[0]
        self._competitors = settings[5]
        query = 'SELECT COUNT(1) FROM TOURNAMENT WHERE TOURNAMENT_ID=%s'
        data = (self._tournament_id,)
        self._cursor.execute(query, data)
        result = self._cursor.fetchone()
        print ' ---Setting Tournament---'
        if int(result[0]) >= 1:
            print 'Tournament Id already registered, getting new one from seq'
            query = '''select nextval('id_tournament_sequence')'''
            self._cursor.execute(query)
            result = self._cursor.fetchone()
            print 'The new Tournament Id is[', result[0], ']'
            self._tournament_id = result[0]
            settings[0] = result[0]
        print settings
        # range of competitors to define number of rounds to get top 8
        rang_ini = [3, 5, 9, 17, 33, 65, 128, 227]
        rang_fin = [4, 8, 16, 32, 64, 128, 226, 409]
        x, aux_round = 0, 2
        for i in rang_ini:
            if self._competitors in xrange(i, rang_fin[x]+1):
                self._total_rounds = aux_round
                break
            aux_round += 1
            x += 1
        if self._competitors > 409:
            self._total_rounds = 10            
        query = 'INSERT INTO TOURNAMENT (TOURNAMENT_ID, TOURNAMENT_NAME, \
            TOURNAMENT_PLACE, START_DATE, END_DATE,NUMBER_COMPETITORS) \
            VALUES (%s,%s,%s,%s,%s,%s);'
        self._cursor.execute(query, settings)
        self._connection.commit()
        print 'Number of rounds to the Tournament [',self._total_rounds,']'

    def rankingInit(self):
        ''' Adds an initial ranking randomly for the first round by shuffling

        According to Swiss-Style the competitors registered in the tournament
        must be shuffled for the first round. In order to support multi-tournaments
        the players must be registered to the tournament.
        '''
        if self._statusInit == False:
            j = 1
            query = 'SELECT PLAYER_ID FROM PLAYERS_TOURNAMENT \
                     WHERE TOURNAMENT_ID=%s'
            data = (self._tournament_id,)
            self._cursor.execute(query, data)
            rows = self._cursor.fetchall()
            random.shuffle(rows)  # Shuffle the list of players
            query = 'UPDATE PLAYERS_TOURNAMENT SET RANK_INI=%s \
                     WHERE PLAYER_ID=%s AND TOURNAMENT_ID=%s'
            # Each player registers to the tournament, according to the list randomly
            # it assigns a consecutive ranking since 1
            for x in rows:
                data = (j, x[0], self._tournament_id)
                self._cursor.execute(query, data)
                self._connection.commit()
                j += 1
            self._statusInit = True
            self._round = 1

    def reportMatchExtend(self, winner, loser, round_, date_match):
        '''Records the outcome of a single match between two players.
        This is an extended method of reportMatch to support multi-tournaments
        and register the date of the match. The commit statement must be
        responsible of the designer outside the method, to make the 
        application faster

        Args:
          winner:  the id number of the player who won
          loser:  the id number of the player who lost
        '''
        query = 'INSERT INTO MATCHES (TOURNAMENT_ID, ROUND, DATE_MATCH, WINNER,\
                 LOSER) VALUES (%s,%s,%s,%s,%s);'
        data = (self._tournament_id, round_, date_match, winner, loser, )
        self._cursor.execute(query, data)

    def closeConnect(self):
        ''' Close the connection to the database tournament'''

        self._connection.close()
        print 'Connection is closed'

    def rollback(self):
        ''' Rollback transaction'''
        self._connection.rollback()        
