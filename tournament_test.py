#!/usr/bin/env python
#
# Test cases for tournament.py

import tournament
import names
import datetime
import random
import time

def testDeleteMatches():
    conn_tournmt.deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    c = conn_tournmt.countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    print ("register player")
    conn_tournmt.registerPlayer("Chandra Nalaar")
    c = conn_tournmt.countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    conn_tournmt.registerPlayer("Markov Chaney")
    conn_tournmt.registerPlayer("Joe Malik")
    conn_tournmt.registerPlayer("Mao Tsu-hsi")
    conn_tournmt.registerPlayer("Atlanta Hope")
    c = conn_tournmt.countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    conn_tournmt.deletePlayers()
    c = conn_tournmt.countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    conn_tournmt.registerPlayer("Melpomene Murray")
    conn_tournmt.registerPlayer("Randy Schwartz")
    conn_tournmt.rankingInit()
    standings = conn_tournmt.playerStandings()
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
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    conn_tournmt.registerPlayer("Bruno Walton")
    conn_tournmt.registerPlayer("Boots O'Neal")
    conn_tournmt.registerPlayer("Cathy Burton")
    conn_tournmt.registerPlayer("Diane Grant")
    conn_tournmt.rankingInit()
    standings = conn_tournmt.playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    conn_tournmt.reportMatch(id1, id2)
    conn_tournmt.reportMatch(id3, id4)
    standings = conn_tournmt.playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match lenoser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    conn_tournmt.deleteMatches()
    conn_tournmt.deletePlayers()
    conn_tournmt.registerPlayer("Twilight Sparkle")
    conn_tournmt.registerPlayer("Fluttershy")
    conn_tournmt.registerPlayer("Applejack")
    conn_tournmt.registerPlayer("Pinkie Pie")
    standings = conn_tournmt.playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    conn_tournmt.reportMatch(id1, id2)
    conn_tournmt.reportMatch(id3, id4)
    pairings = conn_tournmt.swissPairings()
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
    print "Number of competitors [",conn_tournmt._competitors,"]"
    for i in range(conn_tournmt._competitors):
        # register players' name randomly using the module names     
        conn_tournmt.registerPlayer(names.get_full_name())
    testRandomInit()
    while id_round <=conn_tournmt._total_rounds:
        print "Round=[",id_round,"]"        
        swiss= conn_tournmt.swissPairingsExtend()
        print "\n"
        print "Next match=",swiss
        print "\n"
        current_date = datetime.datetime.now()
        current_date= current_date.replace(microsecond=0)
        for z in range(len(swiss)):
            winner=random.randint(0,1)
            if winner==0:
                losser=2
            else:
                losser=0
                winner=2
            conn_tournmt.reportMatchExtend(swiss[z][winner],swiss[z][losser],
                id_round,current_date)        
        conn_tournmt._connection.commit()
        id_round +=1    
    conn_tournmt.closeConnect()
    print("Total execution --- %s seconds ---" % (time.time() - start_time))


def testRandomInit():
    conn_tournmt.rankingInit()


if __name__ == '__main__':
    print " ---Starting Tournament---"
    #Define settings of the tournament, required for testTournamentMultiPlayers
    #[tournmt_id,tournmt_name,location,date_start,date_end,number_competitors]
    data=[1234,'Tournament swissPairings','Mexico city','2015-12-01',
          '205-12-30',17]
    # Udacity test nanodegree program      
    conn_tournmt=tournament.TournamentSwissDb()
    conn_tournmt.connect()
    conn_tournmt.setTournamentInfo(data)
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testRandomInit()
    testStandingsBeforeMatches()
    reportMatches()
    testPairings()
    
    # Test extended implementation (multi-players and multi-tournaments)
    #testTournamentMultiPlayers()
    
    print "Success!  All tests pass!"


