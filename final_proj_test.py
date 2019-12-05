import unittest
from final_project import *
import json


class Testdata(unittest.TestCase):

    def testJSON(self):
        JSON_NAME = 'players.json'
        json_file = open(JSON_NAME, 'r')
        json_contents = json_file.read()
        JSON_DICTION = json.loads(json_contents)
        json_file.close()
        player1=JSON_DICTION[0]
        self.assertEqual(player1['rank'], '1')
        self.assertEqual(player1['Name of Server'], "BR")
        self.assertEqual(player1['Most played lane'], "Jungle")



class TestDatabase(unittest.TestCase):

    def test_player_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT NameofServer FROM Players'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('BR',), result_list)
        self.assertEqual(len(result_list), 220)

        sql = '''
            SELECT Mostplayedlane FROM Players
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Top',), result_list)
        self.assertEqual(len(result_list), 220)

        conn.close()

    def test_server_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Servername
            FROM Servers
            WHERE Abbreviation="BR"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Brazil',), result_list)
        self.assertEqual(len(result_list), 1)

        sql = '''
            SELECT COUNT(*)
            FROM Servers
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 10 or count == 11)

        conn.close()


class TestplayerSearch(unittest.TestCase):

    def test_player_search(self):
        results = process_command('player server=BR')
        self.assertEqual(results[0][1], 1)

        results = process_command('player lane=mid')
        self.assertEqual(results[0][5], 'Mid')

        results = process_command('player server=BR bottom=3')
        self.assertEqual(results[0][1], 20)
        try:
            process_command( 'player server = br lane = mid bar point')
        except:
            self.fail()



class TestserverSearch(unittest.TestCase):

    def test_server_search(self):
        results = process_command('server ')
        self.assertEqual(results[0][1], 'BR')
        self.assertEqual(results[0][0], 'Brazil')
        results = process_command('server best')
        self.assertEqual(results[0][1], 'BR')
        self.assertEqual(results[0][0], 'Brazil')
        self.assertEqual(results[3][1], 'JP')
        self.assertEqual(results[3][0], 'Japan')
        try:
            process_command('server horizontal')
        except:
            self.fail()
if __name__ == '__main__':
    unittest.main()
