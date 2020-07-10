#common.py: common functions used throughout the backend and frontend organized into classes in one file, eliminating global variables, 
#increasing readability, and reducing file size.

from cryptography.fernet import Fernet
import pymysql.cursors
import datetime

#start of class
class db:
    #set variables used throughout class
    decrypted_databasepassword = ""
    dbobj = ""
    dbc = ""
    def __init__(self):
        #ran when an instance of this class is created
        #decrypts database password
        with open("k.txt", "r") as kfile:
            self.key = kfile.readline()
        with open("dbp.txt", "r") as dbpfile:
            #get encrypted data from file
            encrypted_data = dbpfile.readline()
            #create an instance of Fernet
            f = Fernet(self.key)
            #self refers to this class, so any variable defined outside functions becomes self.<name>, and can be accessed from anywhere in the class. 
            #in this case, we need the decrypted database password to be accessible from anywhere in the class, like the connect function below.
            #this uses Fernet to decrypt the password
            self.decrypted_databasepassword = f.decrypt(encrypted_data.encode('UTF-8'))
    
    def connect(self, database):
        #connect to db, this instance is also self.<name> because it needs to be accessible from elsewhere in the class
        self.dbobj=pymysql.connect(host='10.0.0.51',
                    user="tk421bsod",
                    password=self.decrypted_databasepassword.decode(),
                    db=database,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True)
        #creates a cursor object, which then can be used to execute sql queries
        #again, this needs to be accessible from elsewhere in the class
        self.dbc=self.dbobj.cursor()

    def insert(self, database, table, valuesdict, valuenodupe, debug, valueallnum, valueallnumenabled):
        #maximilian-api-savechanges.py passes data to this, where it concatenates lists of values to insert, value placeholders, and checks if data is valid and has no duplicates.
        #this is one of the only functions that actually connects to a db
        #try to execute this code, if an exception occurs, stop execution of this function and execute code in the Except block at the bottom
        try:
            #connect to db
            if debug == False:
                self.connect(database)
            else:
                pass
            #for each key and value, join them together with a comma and space
            print("concatenating value names")
            valuenames = ', '.join(list(valuesdict.keys()))
            print("concatenating values to insert")
            #use one %s for each key as a placeholder
            print("concatenating placeholders")
            valuenameplaceholders = ', '.join([f'{i}' for i in list(valuesdict.keys())])
            valueplaceholders = ', '.join(['%s' for i in list(valuesdict.values())])
            values =  ', '.join([i for i in list(valuesdict.values())])
            print(values)
            valueslist = list(valuesdict.values())
            print(str(valueslist))
            print("concatenating inserttokens")
            #then put it all together (append each item to a list, one at a time, except for placeholders)
            #for every key, there's a value, so the same amount of placeholders should be used for both keys and values
            print("concatenating query")
            sql = f"insert into {table} (" + valuenameplaceholders + ") values (" + valueplaceholders + ")"
            #if debug is enabled (set to true), print out some debugging information and exit
            if debug == True:
                print("Value Names: " + str(valuenames))
                print("Placeholders: " + str(valuenameplaceholders))
                print("Data to insert: " + str(values))
                print("Table: " + str(table))
                print("SQL Query: " + str(sql))
                print("Exiting...")
                return "debuginfoprinted"
            #if debug is disabled (set to false)
            print("checking if valueallnum is enabled")
            if debug == False:
                if valueallnumenabled == True:
                    try:
                        checkallnum = int(valuesdict[valueallnum])
                    except Exception as e:
                        return "error-valuenotallnum"
                print('checking for duplicates')
                #get the number of rows with duplicate values, valuenodupe is the value that distinguishes rows (like response_trigger for responses)
                self.dbc.execute("select count(*) from {} where {}=%s".format(table, valuenodupe), (valuesdict[valuenodupe]))
                #set a variable to that result
                row = self.dbc.fetchone()
                #if the number of rows is greater than 0,
                print("nearly finished checking for duplicates")
                if row['count(*)'] > 0:
                    #there's a duplicate
                    #if there's a duplicate, exit and return an error message
                    return "error-duplicate"
                else:
                    print("no duplicates found")
                    print(sql)
                    print("insert into passwords (" + valuenameplaceholders + ") values (" + valueslist + ")")
                    print(sql)
                    print(valueslist)
                    print(str(valueslist))
                    print(str(valueslist).replace("[", "").replace("]", ""))
                    self.dbc.execute(sql, (valueslist))
                    print("data inserted")
                    #then close the connection (since autocommit = True, changes don't need to be commited)
                    self.dbobj.close()
                    #and exit, showing that it succeeded
                    return "success"
        #if an exception occurs, assign that exception message to a variable
        except Exception as e: 
            #then print it and log the event to a file
            print("Error: " + e + ". Exiting...")
            with open("exceptiondump.txt", "a") as dumpfile:
                dumpfile.write("\n An exception occurred while inserting data into the database at " + str(datetime.datetime.now()) + ".\n The exception was " + str(e) + ". Check the log file for more details.")
            #and return an error message
            return "error-unhandled"
    
    def retrieve(self, database, table, valuenametoretrieve, retrievedvalue, valuetoretrieve, debug):
        self.connect(database)
        print("Value to retrieve: " + str(valuetoretrieve))
        print("Table: " + str(table))
        print("Value name: " + str(valuenametoretrieve))
        print("Value = " + str(retrievedvalue))
        print("SQL Query: select " + valuetoretrieve + " from " + table + " where " + valuenametoretrieve + "=" + retrievedvalue)
        self.dbc.execute("select {} from {} where {}=%s".format(valuetoretrieve, table, valuenametoretrieve), (retrievedvalue))
        row = self.dbc.fetchone()
        if debug == True:
            print(str(row))
            return row
        return row
class token:
    def decrypt(self):
        with open("token.txt", "r") as tokenfile:
            with open("k.txt", "r") as kfile:
                self.key = kfile.readline()
            #use fernet to decrypt token, returning token
            encrypted_token = tokenfile.readline()
            f = Fernet(self.key)
            decrypted_token = f.decrypt(encrypted_token.encode('UTF-8'))
            return decrypted_token.decode()
