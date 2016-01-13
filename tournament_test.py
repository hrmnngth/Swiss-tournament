#!/usr/bin/env python
#
# Test cases for tournament.py

import tournament
import names
import datetime
import random
import time

def testDeleteMatches():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    c = swiss_trnmnt.conn_trnmt_db.countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    print ("register player")
    swiss_trnmnt.registerPlayer("Chandra Nalaar")
    c = swiss_trnmnt.conn_trnmt_db.countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    swiss_trnmnt.registerPlayer("Markov Chaney")
    swiss_trnmnt.registerPlayer("Joe Malik")
    swiss_trnmnt.registerPlayer("Mao Tsu-hsi")
    swiss_trnmnt.registerPlayer("Atlanta Hope")
    c = swiss_trnmnt.conn_trnmt_db.countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    c = swiss_trnmnt.conn_trnmt_db.countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    swiss_trnmnt.registerPlayer("Melpomene Murray")
    swiss_trnmnt.registerPlayer("Randy Schwartz")
    standings = swiss_trnmnt.playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def reportMatches():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    swiss_trnmnt.registerPlayer("Bruno Walton")
    swiss_trnmnt.registerPlayer("Boots O'Neal")
    swiss_trnmnt.registerPlayer("Cathy Burton")
    swiss_trnmnt.registerPlayer("Diane Grant")
    standings = swiss_trnmnt.playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    swiss_trnmnt.reportMatch(id1, id2)
    swiss_trnmnt.reportMatch(id3, id4)
    standings = swiss_trnmnt.playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match lenoser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    swiss_trnmnt.conn_trnmt_db.deleteMatches()
    swiss_trnmnt.conn_trnmt_db.deletePlayers()
    swiss_trnmnt.registerPlayer("Twilight Sparkle")
    swiss_trnmnt.registerPlayer("Fluttershy")
    swiss_trnmnt.registerPlayer("Applejack")
    swiss_trnmnt.registerPlayer("Pinkie Pie")
    standings = swiss_trnmnt.playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    swiss_trnmnt.reportMatch(id1, id2)
    swiss_trnmnt.reportMatch(id3, id4)
    pairings = swiss_trnmnt.swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."
        

def testTournamentMultiPlayers():
    id_round=1
    start_time = time.time()
    final_players= list()
    print "Number of participants [",swiss_trnmnt._participants,"]"
    for i in range(swiss_trnmnt._participants):
        # register players' name randomly using third-package names
        try:
            swiss_trnmnt.registerPlayer(names.get_full_name())
        except Exception as ex:
            swiss_trnmnt.rollback()
            if ex.pgcode == '23505': # avoit duplicated player in same tournamnt
                swiss_trnmnt.registerPlayer(names.get_full_name())
            else:
                raise Exception('Unexpected error registering players',str(ex)) 
    swiss_trnmnt.rankingInit()
    while id_round <=swiss_trnmnt._total_rounds:
        print "Round=[",id_round,"]"
        # result of pairings for next match [(id1,name1,id2,name2),...]     
        swiss= swiss_trnmnt.swissPairings() 
        print '\n'
        print "Next match=",swiss,'\n'
        testMatchesRandomly(swiss,id_round) # establish winner of match randomly          
        id_round +=1
    print '--- SWISS TOURNAMENT FINISHED ---\n'
    print '   Final Standings'
    print ('ID\tNAME\t\tWINS')
    print ('---------------------------')
    final_stands=swiss_trnmnt.playerStandings()
    for i in final_stands:
        print i[0],'\t',i[1][:13],'\t',i[2] # it prints ID | NAME | WINS
    final_players=swiss_trnmnt.topEightPlayers()
    print (''' \nThe final TOP players using opponents-points for tie-break''')
    print ('ID\tNAME\t    POSITION')
    print ('---------------------------')
    x=1    
    for top8 in final_players:
        for rows in top8:
            print rows[0],'\t',rows[1][:10],'\t',x
            x+=1    
    print '\n---Starting single-elimination tournament---'  
    while id_round <=swiss_trnmnt._total_rounds+swiss_trnmnt._rounds_single: # round's number for single is 3
        print "Round final=[",id_round,"]" 
        single= swiss_trnmnt.siglePairingElimination()        
        print "Next match=",single, '\n'    
        testMatchesRandomly(single,id_round) # establish winner of match randomly
        id_round +=1
    swiss_trnmnt.setWinnerTournament()
    swiss_trnmnt.closeTournament()
    print("Total execution --- %s seconds ---" % (time.time() - start_time))


def testMatchesRandomly(pairings,id_round):
    current_date = datetime.datetime.now()
    current_date= current_date.replace(microsecond=0)
    for z in range(len(pairings)):
        winner=random.randint(0,1)
        if winner==0:
            losser=2
        else:
            losser=0
            winner=2
        swiss_trnmnt.reportMatch(pairings[z][winner],pairings[z][losser],
            id_round,current_date)        
    swiss_trnmnt.commitTournament()   


if __name__ == '__main__':
    print " -----   STARTING SWISS-TOURNAMENT   -----"
    #Define settings of the tournament, required for testTournamentMultiPlayers
    #[tournmt_id,tournmt_name,location,date_start,date_end,number_participants]
    data=[1234,'swiss_trnmnt swissPairings','Mexico city','2015-12-01',
          '205-12-30',19]     
    swiss_trnmnt=tournament.Swiss()
    swiss_trnmnt.setTournamentInfo(data)

    # Udacity test nanodegree program
    '''testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    reportMatches()
    testPairings()
    '''
    # To test extended implementation (multi-players and multi-tournaments) 
    # "comment methods for testing nanodegree program"
    
    testTournamentMultiPlayers()
    
    print "Success!  All tests pass!"


