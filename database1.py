class Database():

    def __init__(self):
        self.conn = sqlite3.connect(r'D:\DBfolder\exp_database.db')
        self.cursor = self.conn.cursor()

    def create_database_stucture(self, list_of_articles, links_for_articles):
        database_stucture = []
        for i in range(len(list_of_articles)):

            for j in range(len(list_of_articles[i])):
                line = []
                line.append(links_for_articles[i][j])
                for k in range(len(list_of_articles[i][j])):
                    line.append(list_of_articles[i][j][k])
                database_stucture.append(line)
        return database_stucture

    def create_database(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS database(
                       link TEXT PRIMARY KEY,
                       text TEXT,
                       date TEXT,
                       tags TEXT);
                        """)
        self.conn.commit()

    def insert_database(self, list_of_articles, links_for_articles):
        sql = """INSERT INTO database(link,text,date,tags) VALUES (?, ?, ?, ?) """
        database_structure = self.create_database_stucture(list_of_articles, links_for_articles)
        for i in database_structure:
            self.cursor.execute(sql, i)
        self.conn.commit()

    def get_request(self):
        request = str(input('Ваш запрос: '))
        self.cursor.execute(request)
        results = self.cursor.fetchall()
        return print(results)


db = Database()

a = db.create_database_stucture(list_of_articles, links_for_articles)


db.create_database()

db.insert_database(list_of_articles, links_for_articles)

db.get_request()




