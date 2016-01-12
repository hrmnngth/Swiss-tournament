#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import collections
import random
import player
import datetime
import xml.etree.ElementTree as ET


class Tournament(object):

    ''' Class object Tournament that implements the logic to create a Tournament
        It contains methods to inicialize the tournament, register players,
        report matches, get standings.
    '''

    def __init__(self):
        ''' inicialize the class and create an instance of TournamentDb
        '''
        self.statusConnect = False
        self.conn_trnmt_db = TournamentDb()
        self.conn_trnmt_db.connect()
        self._tournament_id = None
        self._statusInit = False
        self._round = 0
        self._total_rounds = 0
        self._competitors = 0

    def setTournamentInfo(self, settings):
        '''Define an id for the tournament,in order to support multi-tournaments

        The information is store in the database, it has relation with players,
        matches and the standings, in order to support multi-tournaments with 
        the players already registered. At the beggining the winner 
        and second place are not defined.

        Args:
          data: (list) an structure of values for setting the tournament 
                [id,tournament's name, tournament's place, date_start, date_end, 
                number of competitors, winner (None), second place (None)]
        '''
        self._tournament_id = settings[0]
        self._competitors = settings[5]
        query = 'SELECT COUNT(1) FROM TOURNAMENT WHERE TOURNAMENT_ID=%s'
        data = (self._tournament_id,)
        self.conn_trnmt_db._cursor.execute(query,data)
        result = self.conn_trnmt_db._cursor.fetchone()
        print ' ---Setting Tournament---'
        if (result[0]) >= 1:
            print 'Tournament Id already registered, getting new one from seq'
            query = '''SELECT NEXTVAL('ID_TOURNAMENT_SEQUENCE')'''
            self.conn_trnmt_db._cursor.execute(query)
            result = self.conn_trnmt_db._cursor.fetchone()
            print 'The new Tournament Id is[', result[0], ']'
            self._tournament_id = result[0]
            settings[0] = result[0]
        print settings
        # range of competitors to define number of rounds acording to swiss-system 
        rang_ini = [3, 5,  9, 17, 33,  65, 128, 227]
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
        self.conn_trnmt_db.dbStatementCommit(query, settings)
        print 'Number of rounds to the Tournament [', self._total_rounds, ']'

    def rankingInit(self):
        ''' Adds an initial ranking randomly for the first round by shuffling

        According to Swiss-Style the competitors registered in the tournament
        must be shuffled for the first round. In order to support 
        multi-tournaments the players must be registered to the tournament.
        '''
        if self._statusInit == False:            
            query = 'SELECT PLAYER_ID FROM PLAYERS_TOURNAMENT \
                     WHERE TOURNAMENT_ID=%s'
            data = (self._tournament_id,)
            result = self.conn_trnmt_db.dbQuery(query, data)
            random.shuffle(result)  # Shuffle the list of players
            query = 'UPDATE PLAYERS_TOURNAMENT SET RANK_INI=%s \
                     WHERE PLAYER_ID=%s AND TOURNAMENT_ID=%s'
            # Each player registers to the tournament, according to the list 
            # randomly, it assigns a consecutive ranking since 1
            j = 1
            for x in result:
                data = (j, x[0], self._tournament_id)
                self.conn_trnmt_db.dbStatementCommit(query, data)
                j += 1
            self._statusInit = True
            self._round = 1

    def reportMatch(self, winner, loser, round_=None, date_match=None):
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
        self.conn_trnmt_db._cursor.execute(query, data)

    def checkAlreadyRegistered(self, name):
        '''Verifies if player already registered in the DB

        Args:
            name: (string) the player's full name 
        returns:
            if exists returns the id of the player otherwise 0
        '''
        query = 'SELECT PLAYER_ID FROM PLAYERS WHERE FULL_NAME=%s'
        data = (name,)
        result = self.conn_trnmt_db.dbQuery(query, data)
        if result and result[0] > 0:
            return result[0]
        return 0

    def playerStandings(self):
        '''Returns a list of the players and their win records, sorted by wins.
           It supports multi-tournaments and multip-players

        The first entry in the list should be the player in first place, 
        or a player tied for first place if there is currently a tie.
        Returns:
          A list of tuples, each of which contains (id, name, wins, matches):
            id: the player's unique id (assigned by the database)
            name: the player's full name (as registered)
            wins: the number of matches the player has won
            matches: the number of matches the player has played
        '''
        standings = list()
        player_standings = collections.namedtuple(
            'playerStandings', 'id, name, wins, matches')
        query = 'SELECT PLAYER_ID,FULL_NAME, WINS,MATCHES FROM V_STANDINGS \
                 WHERE TOURNAMENT_ID=%s'
        data = (self._tournament_id,)
        self.conn_trnmt_db._cursor.execute(query, data)
        # Adds the result of standings to the collection
        for rows in map(player_standings._make,
                        self.conn_trnmt_db._cursor.fetchall()):
            standings.append(rows)
        return standings

    def registerPlayer(self, name):
        '''Adds a player to the tournament database.

        The database assigns a unique serial id number for the player.  (This
        is handled by the SQL database schema using ID_PLAYER_SEQUENCE.)
        Args:
          name: the player's full name (need not be unique).
        '''
        c = self.checkAlreadyRegistered(name)
        if c > 0:
            # If exist the player (name) only to update the last tournament
            # that it's participating
            query = 'UPDATE PLAYERS SET LAST_TRNMNT_RGSTRD=%s \
                     WHERE PLAYER_ID=%s'
            data = (self._tournament_id, c)
            self.conn_trnmt_db.dbStatementCommit(query, data)
        else:
            # Register as new player in the database
            query = '''INSERT INTO PLAYERS (PLAYER_ID, FULL_NAME, \
            LAST_TRNMNT_RGSTRD) VALUES (nextval('id_player_sequence'),%s,%s);'''
            data = (name, self._tournament_id)
            self.conn_trnmt_db.dbStatementCommit(query, data)

    def previusMatch(self, player1, player2):
        '''Verify if the opponents have already matched

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
        query = 'SELECT COUNT(1)TOT FROM MATCHES WHERE TOURNAMENT_ID=%s \
                AND WINNER IN(%s,%s) AND LOSER IN(%s,%s)'
        data = (self._tournament_id, player1, player2, player1, player2)
        self.conn_trnmt_db._cursor.execute(query,data)
        result = self.conn_trnmt_db._cursor.fetchone()
        if result[0] > 0:
            matchedBoolean = True
        return matchedBoolean    

    def siglePairingElimination(self):
        '''Create a sub-tournament with top 8 players to determine the winner
        This sub-tournament has tree rounds based on the number of players (8)

        Returns
          pairings: (list) for each round returns a list of pairings 
                    for the match
        '''
        pairings = list()
        if self._total_rounds+1 == self._round:
            query = 'SELECT PLAYER_ID, FULL_NAME FROM V_STANDINGS \
            WHERE TOURNAMENT_ID=%s AND RANK_FIN >0 AND RANK_FIN<=8 \
            ORDER BY RANK_FIN'
            data = (self._tournament_id,)
        else:
            query = 'SELECT C.PLAYER_ID, C.FULL_NAME \
                FROM MATCHES A, PLAYERS_TOURNAMENT B, V_STANDINGS C \
                WHERE A.WINNER=B.PLAYER_ID AND B.PLAYER_ID=C.PLAYER_ID \
                AND A.ROUND=%s AND B.RANK_FIN >0 AND B.RANK_FIN<=8 \
                AND A.TOURNAMENT_ID=B.TOURNAMENT_ID \
                AND B.TOURNAMENT_ID=C.TOURNAMENT_ID \
                AND B.TOURNAMENT_ID=%s'
            data = (self._round-1, self._tournament_id)
        result = self.conn_trnmt_db.dbQuery(query, data)
        len_res = len(result)
        group_a, group_b = result[:len_res/2], result[len_res/2:]
        revers = reversed(group_b)
        for i in group_a:
            j = next(revers)
            pairings.append((i[0], i[1], j[0], j[1]))
        self._round += 1

        return pairings

    def setWinnerTournament(self):
        ''' Update the winner and second place of the tournament in the DB

        After finished the single-elimination-tournament should be invoke this
        method to update in the table Tournament the winner and second place. 
        It uses xml data to store values (player_id,full_name), this might be
        useful for future use in a web page

        '''
        xmlTemplate = """<root><player><id>%(player_id)s</id> \
                        <name>%(full_name)s</name></player></root>"""
        query = '''SELECT 'player_id' AS ID,WINNER ,'full_name' AS NAME, \
                FULL_NAME FROM MATCHES A, PLAYERS B \
                WHERE TOURNAMENT_ID=%s AND WINNER=PLAYER_ID AND ROUND=%s'''
        data = (self._tournament_id, self._total_rounds+3)
        result = self.conn_trnmt_db.dbQuery(query, data)
        for i in result:
            result = list(i)
        it = iter(result)
        winner = xmlTemplate % dict(zip(it, it))
        query = '''SELECT 'player_id' AS ID,loser ,'full_name' AS NAME, \
                FULL_NAME FROM MATCHES A, PLAYERS B \
                WHERE TOURNAMENT_ID=%s AND LOSER=PLAYER_ID AND ROUND=%s'''
        data = (self._tournament_id, self._total_rounds+3)
        result = self.conn_trnmt_db.dbQuery(query, data)
        for i in result:
            result = list(i)
        it = iter(result)
        second_place = xmlTemplate % dict(zip(it, it))

        query = 'UPDATE TOURNAMENT SET WINNER=%s, SECOND_PLACE=%s \
                     WHERE TOURNAMENT_ID=%s'
        data = (winner, second_place, self._tournament_id)
        self.conn_trnmt_db.dbStatementCommit(query, data)
        root = ET.fromstring(winner)
        for elem in root.findall('player'):
            name_winner = elem.find('name').text
        print 'The WINNER OF THE TOURNAMENT IS [', name_winner, ']'
        print '\n'

    def closeTournament(self):
        self.conn_trnmt_db.closeConnect()

    def commitTournament(self):
        self.conn_trnmt_db.commit()

    def rolllbackTournament(self):
        self.conn_trnmt_db.rollback()


class Swiss(Tournament):

    ''' Class extended from Tournament that implements the logic to create a 
        swiss tournament. It has methods to get pairings, to set a round bye
        in case of odd competitors, and a method to break tied stands
    '''

    def __init__(self):
        self.statusConnect = False
        Tournament.__init__(self)

    def swissPairings(self):
        '''Returns a list of pairs of players for the next round of a match.
           It supports multip-players and multi-tournaments

        Assuming that there are an even number of players registered, each player
        appears exactly once in the pairings.  Each player is paired with another
        player with an equal or nearly-equal win record, that is, a player adjacent
        to him or her in the standings. If a player got a round bye, in the next
        round it has the hightest priority to make the first match 

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
        players_bye = list()
        query_stands = self.playerStandings()
        # Convert the list (query_stands) into dictionary and create the pairs for the
        # next round randomly; it takes WINS as key. If there are an odd number,
        # assigns the last player of dictionary to a round bye.
        # Make match with priority (player-round_bye), avoids to pair players
        # again
        v_stndgs = collections.defaultdict(list)
        for i, n, w, m in query_stands:
            # win-->key,(player object)-->item-info
            v_stndgs[w].append(player.Player(w, i, n, m))
        max_len_stnds = len(v_stndgs)
        count_keys = 1
        print '--- Standings (id,name,wins) ---'
        players_bye = self.getPlayersBye(self._tournament_id)
        for k in v_stndgs.iterkeys():
            for w in v_stndgs[k]:
                print w.getPlayerId(), '|', w.getName()[:10], '|', w.getWins()
            pairings_tmp = list()
            alrdy_match = True
            match_with_bye = False
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
                        print 'Player with round bye'
                        print (actual_player.getPlayerId(),
                               actual_player.getName())
                        self.roundBye(actual_player, self._round)
                    else:
                        # make pairing last player of previous key with the
                        # last one of dict
                        val_rndm = 0
                        pairings_tmp.append((prev_last_player.getPlayerId(),
                                             prev_last_player.getName(),
                                             v_stndgs[k][
                                                 val_rndm].getPlayerId(),
                                             v_stndgs[k][val_rndm].getName()))
                        del v_stndgs[k][val_rndm]
                        prev_last_player = []
                        break
                if tot_items == 1:  
                    # last player of the list, no more players with same standing
                    # to be paired. it will be used in the next highest standing
                    prev_last_player = actual_player
                    break
                if not prev_last_player:
                    cnt = 0
                    # get the opponent based on priority, first from
                    # all player that had a  previous bye
                    # the result is the position in the current list
                    oppnt_player = self.checkPlayersBye(
                        v_stndgs[k][1:], players_bye)
                    if oppnt_player >-1: oppnt_player+=1
                    val_rndm, match_with_bye = self.valOponent(
                        oppnt_player, tot_items)                                        
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
                            match_with_bye = False
                            players_bye = self.getPlayersBye(
                                self._tournament_id)
                            break
                        if alrdy_match == True:
                            val_rndm = random.randint(1, tot_items-1)
                            match_with_bye = False
                        cnt += 1
                    else: # if it doesn't exist a previous match
                        alrdy_match = True
                        if match_with_bye == True:
                            # if the opponent is a player-bye it removes from list
                            players_bye.remove(
                                (v_stndgs[k][val_rndm].getPlayerId(),))
                            match_with_bye = False
                        pairings_tmp.append((actual_player.getPlayerId(),
                                             actual_player.getName(),
                                             v_stndgs[k][
                                                 val_rndm].getPlayerId(),
                                             v_stndgs[k][val_rndm].getName()))
                        # delete the opponents of the list after they got
                        # paired
                        del v_stndgs[k][val_rndm]
                        del v_stndgs[k][0]

                else:
                    # This block make pairing between last player of previous
                    # key and it seeks a opponent base on priority
                    oppnt_player = self.checkPlayersBye(
                        v_stndgs[k], players_bye)
                    val_rndm, match_with_bye = self.valOponent(
                        oppnt_player, tot_items)
                    while alrdy_match:
                        alrdy_match = self.previusMatch(
                            prev_last_player.getPlayerId(),
                            v_stndgs[k][val_rndm].getPlayerId())
                        if alrdy_match == True:
                            val_rndm = random.randint(0, tot_items-1)
                            match_with_bye = False
                    else:
                        alrdy_match = True
                        if match_with_bye == True:
                            players_bye.remove(
                                (v_stndgs[k][val_rndm].getPlayerId(),))
                            match_with_bye = False
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

    def valOponent(self, oppnt_player, tot_items):
        ''' Verify if the id of the opponent coming after examine the players 
            with byes. if it is -1 means that there are not bye players, in this
            case it gets an opponent randonmly
        Args:
          oppnt_player: (int) id from the result of checkPlayersBye
          tot_items: (int) the len of the current list
        returns:
          val_rndm,match_with_bye: (int,int) a compose of values necessary to 
                                    continue the logic of swissPairings method
        '''
        match_with_bye = False
        if oppnt_player == -1:
            val_rndm = random.randint(1, tot_items-1)
        else:
            val_rndm = oppnt_player
            match_with_bye = True
        return val_rndm, match_with_bye

    def roundBye(self, player, round_):
        ''' Sets up a player-round-bye when there are an odd number of players

        When the number of competitors is not an even number, according to 
        Swiss-Style Pairing rules it establishes after pairings are completed
        the player remaining receives a bye, equaling one match win.

        Args:
          id_player: (int) the player's unique id
          round_: (int) the round's id
        '''
        current_date = datetime.datetime.now()
        current_date = current_date.replace(microsecond=0)
        loser = 0
        self.reportMatch(player.getPlayerId(), loser, round_, current_date)

    def getPlayersBye(self, list_):
        '''Verify if there's a player who had a round bye to be paired

        In order to make pairings, the hightest priority are the players who
        had taken a round bye.
        Args:
          list_: (list) It is the list which contain the players with the 
                same standing
        Returns:
          Index_list: (int) The index in the list if found a player-bye
        '''
        query = 'SELECT WINNER FROM MATCHES where LOSER=0 and \
                TOURNAMENT_ID=%s ORDER BY ROUND DESC'
        data = (self._tournament_id,)
        result = self.conn_trnmt_db.dbQuery(query, data)

        return result

    def checkPlayersBye(self, list_current, list_byes):
        index_list = -1
        for iter1 in list_byes:
            idx = 0
            for iter2 in list_current:
                if iter1[0] == iter2.getPlayerId():                    
                    index_list = idx
                    return index_list
                    break
                idx += 1
        return index_list

    def tieBreakRule(self, wins_select, sum_wins):
        ''' Select players who are tied with same score, using tie-break rule

        In cases where players have same score at the end of the swiss
        tournament, this uses best points-oponents rule to break players
        that are tied
        Args:
          wins_select: (list) a list of group of wins with final standings
          sum_wins: (int) the number of wins that produce tied players
        '''
        # complex query statement to get opponents points of players with same
        # wins. It selects the necessary players with highest points to complete        
        # the top 8 ( check the last part of statement LIMIT %s)
        # the second level to break tied players is players points
        query = 'SELECT PLAYER, SUM(POINTS)TOT_POINTS FROM (\
            SELECT WINNER AS PLAYER,PLAYER_ID,SUM(POINTS)AS POINTS \
            FROM PLAYER_STANDINGS A, MATCHES B\
            WHERE WINNER IN(SELECT PLAYER_ID FROM PLAYER_STANDINGS \
            WHERE WINS=%s AND TOURNAMENT_ID=A.TOURNAMENT_ID ORDER BY POINTS DESC) \
            AND A.PLAYER_ID=B.LOSER AND A.TOURNAMENT_ID=B.TOURNAMENT_ID \
            AND A.TOURNAMENT_ID=%s GROUP BY WINNER,PLAYER_ID \
            UNION ALL \
            SELECT LOSER,PLAYER_ID,SUM(POINTS) FROM PLAYER_STANDINGS A, \
            MATCHES B \
            WHERE LOSER IN(SELECT PLAYER_ID FROM PLAYER_STANDINGS \
            WHERE WINS=%s AND TOURNAMENT_ID=A.TOURNAMENT_ID ORDER BY POINTS DESC) \
            AND A.PLAYER_ID=B.WINNER AND A.TOURNAMENT_ID=B.TOURNAMENT_ID \
            AND A.TOURNAMENT_ID=%s GROUP BY LOSER,PLAYER_ID ORDER BY 1) C \
            GROUP BY PLAYER ORDER BY TOT_POINTS DESC LIMIT %s'
        limit_ = 8-int(sum_wins) # the rest of players necessary to complete the top 8
        data = (wins_select[0], self._tournament_id, wins_select[0],
                self._tournament_id, limit_)
        result = self.conn_trnmt_db.dbQuery(query, data)
        return result

    def topEightPlayers(self):
        ''' Determines the top 8 players after finished the swiss Tournament

        It considers players' points to stablish the ranking. 
        This method calls tie-break-rule to select players who are tied wit 
        same score. 
        Returns:
          final_players: list() The list of 8 players with best standings
        '''
        query = 'SELECT WINS, COUNT(1) AS TOT FROM \
                (SELECT WINS FROM V_STANDINGS WHERE TOURNAMENT_ID=%s \
                ORDER BY WINS DESC, POINTS DESC) A \
                GROUP BY WINS ORDER BY WINS DESC'
        data = (self._tournament_id,)
        result = self.conn_trnmt_db.dbQuery(query, data)
        sum_wins = 0
        sum_aux = 0
        final_players = list()
        for rows in result:
            sum_wins = sum_wins+rows[1]
            if sum_wins <= 8:
                final_players.append(
                    self.conn_trnmt_db.getFinalPlayers(
                        self._tournament_id, rows[0]))
                sum_aux = sum_wins
            else:
                final_players.append(self.tieBreakRule(rows, sum_aux))
                break
        query = 'UPDATE PLAYERS_TOURNAMENT SET RANK_FIN=%s WHERE PLAYER_ID=%s \
                AND TOURNAMENT_ID=%s'
        z = 1
        for x in final_players:
            for y in x:
                data = (z, y[0], self._tournament_id)
                result = self.conn_trnmt_db._cursor.execute(query, data)
                z += 1
        self.conn_trnmt_db.commit()
        return final_players


class TournamentDb(object):

    ''' Class object that implements the logic to work with database Tournament
        It contains methods to connect with, querys, and some useful operations
        on the database.
    '''

    def __init__(self):
        self.statusConnect = False
        self._connection = None
        self._cursor = None

    def connect(self):
        '''Connect to the PostgreSQL database.Returns a database connection'''

        connection = psycopg2.connect(
            'dbname=tournament user=vagrant password=')
        self._connection = connection
        self._cursor = connection.cursor()
        self.statusConnect = True
        print ('connection to DB is open')

    def dbQuery(self, query, data=None):
        if data:
            self._cursor.execute(query, data)
            r = self._cursor.fetchall()
        else:
            self._cursor.execute(query)
            r = self._cursor.fetchall()
        return r

    def dbStatementCommit(self, query, data=None):
        if data:
            self._cursor.execute(query, data)
            self._connection.commit()
        else:
            self._cursor.execute(query)
            self._connection.commit()

    def deleteMatches(self):
        '''Remove all the match records from the database.'''

        query = 'DELETE FROM MATCHES'
        self.dbStatementCommit(query)

    def deletePlayers(self):
        '''Remove all the player records from the database.'''

        query = 'DELETE FROM PLAYERS'
        self.dbStatementCommit(query)

    def countPlayers(self):
        '''Returns the number of players currently registered.

        Returns: 
          total_players: (int) the total count of players
        '''
        query = 'SELECT COUNT(1) as TOTAL_PLAYERS FROM PLAYERS'
        self._cursor.execute(query)
        r = self._cursor.fetchone()
        return r[0]

    def getFinalPlayers(self, trnmnt_id, wins_select):
        ''' Returns players standings from the database with the 
            condition of wins
        Args:
          wins_select: (int) the value of wins to do the query
        '''
        query = 'SELECT PLAYER_ID, FULL_NAME FROM V_STANDINGS WHERE \
                TOURNAMENT_ID=%s AND WINS=%s'
        data = (trnmnt_id, wins_select)
        result = self.dbQuery(query, data)
        return result

    def closeConnect(self):
        ''' Close the connection to the database tournament'''

        self._connection.close()
        print 'Connection is closed'

    def rollback(self):
        ''' Rollback transaction'''
        self._connection.rollback()

    def commit(self):
        self._connection.commit()
