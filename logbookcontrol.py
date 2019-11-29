#!/usr/bin/python3

#################################################################################################
# Programme          :  logbookcontrol                                                      #
# Date de creation   :  24/01/2017                                                              #
#                                                                                               #
# Version du produit : 1.0               Date : 24/01/2017                                      #
#                                                                                               #
## Description: Compare les données d'une marée entre deux bases AVDTH. La fonction prinipale   #
#               est de comparer les données des flux ERS et AVDTH classique.                    #
# Parametres     : Aucun                                                                        #
#                                                                                               #
#################################################################################################
import getopt, sys
import os
import datetime
import pyodbc


class AVDTH():
    """Définition d'une base AVDTH et des requetes pour accèder aux données"""

    def __init__(self, db_filename):
        """
        Initilisation de la classe
        """
        self.database_filename = db_filename
        self.connection = self.__open_connection()

    def get_info(self):
        """
        Retourne une chaine de caractère contenant des infos pertinentes sur la base
        :return:une chaine de caractère
        """
        return "Le nombre de marée dans %s est de %d." % (self.get_name(), self.count_trip()[0])

    def get_name(self):
        """
        Retourne le nom de la base AVDTH
        :return: une chaîne de caractère
        """
        return os.path.basename(self.database_filename)

    def __open_connection(self):
        """
        Ouvre une connexion sur la base de donnée
        :return: la connexion
        """
        connection_string = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s" % self.database_filename
        return pyodbc.connect(connection_string)

    def count_trip(self):
        """
        Compte le nombre de marée dans la base
        :return: le nombre de marée
        """
        cursor = self.connection.cursor()
        cursor.execute("select count(*) from MAREE")
        return cursor.fetchone()

    def count_activity_for_trip(self, c_bat, d_dbq):
        """
        Compte le nombre d'activités dans la base
        :return: le nombre d'activités
        """
        params = [str(c_bat), d_dbq]
        cursor = self.connection.cursor()
        cursor.execute("select count(*) from ACTIVITE WHERE C_BAT= ? AND D_DBQ= ?", params)
        return cursor.fetchone()

    def count_catches_for_trip(self, c_bat, d_dbq):
        """
        Compte le nombre de captures élémentaires pour la marée
        :return: le nombre de captures élémentaires
        """
        params = [str(c_bat), d_dbq]
        cursor = self.connection.cursor()
        cursor.execute("select count(*) from CAPT_ELEM WHERE C_BAT= ? AND D_DBQ= ?", params)
        return cursor.fetchone()     

    def count_activity(self):
        """
        Compte le nombre d'activités dans la base
        :return: le nombre d'activités
        """
        cursor = self.connection.cursor()
        cursor.execute("select count(*) from ACTIVITE")
        return cursor.fetchone()

    def count_elementary_catch(self):
        """
        Compte le nombre de captures élémentaires dans la base
        :return: le nombre de captures élémentaires
        """
        cursor = self.connection.cursor()
        cursor.execute("select count(*) from CAPT_ELEM")
        return cursor.fetchone()

    def find_trip(self, ers_id):
        """
        Trouve la marée correspondant à l'ID ERS
        :param ers_id: l'id ERS de la marée
        :return: la marée
        """
        cursor = self.connection.cursor()
        cursor.execute("select * from maree WHERE c_id_ers= ?", ers_id)
        columns = [column[0] for column in cursor.description]
        results = []
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(zip(columns, row)))
        return results[0]

    def list_all_trips(self):
        """
        Liste les marées présentes dans la base
        :param connection: une session sur la base
        :return: une liste des marées
        """
        cursor = self.connection.cursor()
        cursor.execute("select * from MAREE ORDER BY C_BAT, D_DBQ ASC")
        columns = [column[0] for column in cursor.description]
        results = []
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(zip(columns, row)))
        return results

    def find_all_ers_id(self):
        """
        Liste les marées présentes dans la base
        :param connection: une session sur la base
        :return: une liste des identifiants ers
        """
        cursor = self.connection.cursor()
        cursor.execute("select C_ID_ERS from MAREE ORDER BY C_BAT, D_DBQ ASC")
        columns = [column[0] for column in cursor.description]
        results = []
        return cursor.fetchall()
        # for row in rows:
        #     results.append(dict(zip(columns, row)))
        # return results

    def list_all_activities_from_trip(self, c_bat, d_dbq):
        """
        Liste les activités présentes dans la base pour une marée donnée
        :param c_bat: le code bateau de la marée
        :param c_dbq: la date de débarquement de la marée
        :return: une liste des activités de la marée
        """
        params = [str(c_bat), d_dbq]
        cursor = self.connection.cursor()
        cursor.execute("select * from ACTIVITE WHERE C_BAT= ? AND D_DBQ= ? ORDER BY C_BAT, D_DBQ, D_ACT  ASC",
                       params)
        columns = [column[0] for column in cursor.description]
        results = []
        rows = cursor.fetchall()
        for row in rows:
            d = dict(zip(columns, row))
            if d['H_ACT'] == None:
                d['H_ACT'] = 0
            if d['M_ACT'] == None:
                d['M_ACT'] = 0
            d['D_ACT_FULL'] = d['D_ACT'].replace(hour=d['H_ACT'], minute=d['M_ACT'])
            d['D_ACT'] = d['D_ACT'].replace(hour=0, minute=0)
            d['ID_ACT'] = d['D_ACT'].strftime("%d-%m-%Y") + "[" + str(d['N_ACT']) + "]"            
            d['V_CAPT'] = self.get_weight_catches_from_activities(c_bat, d_dbq, d['D_ACT'], d['N_ACT'])            
            results.append(d)
        return results

    def list_all_catches_from_trip(self, c_bat, d_dbq):
        """
        Liste les captures présentes dans la base pour une marée donnée
        :param c_bat: le code bateau de la marée
        :param c_dbq: la date de débarquement de la marée
        :return: une liste des captures
        """
        params = [str(c_bat), d_dbq]
        cursor = self.connection.cursor()
        cursor.execute("select * from CAPT_ELEM WHERE C_BAT= ? AND D_DBQ= ? ORDER BY C_BAT, D_DBQ, D_ACT  ASC",
                       params)
        columns = [column[0] for column in cursor.description]
        results = []
        rows = cursor.fetchall()
        for row in rows:
            d = dict(zip(columns, row))
            d['D_ACT'] = d['D_ACT'].replace(hour=0, minute=0)
            d['ID_ACT'] = d['D_ACT'].strftime("%d-%m-%Y") + "[" + str(d['N_ACT']) + "]"
            results.append(d)
        return results

    def get_weight_catches_from_activities(self, c_bat, d_dbq, d_act, n_act):
        """
        Retourne le poids des captures pour une activité donnée
        :param c_bat: le code bateau de la marée
        :param c_dbq: la date de débarquement de la marée
        :param d_act: la date d'activité
        :param n_act: le numéro de l'activité
        :return: le poids des captures
        """
        params = [str(c_bat), d_dbq, d_act, str(n_act)]
        cursor = self.connection.cursor()
        cursor.execute("select * from CAPT_ELEM WHERE C_BAT= ? AND D_DBQ= ? AND D_ACT= ? AND N_ACT= ? ORDER BY C_BAT, D_DBQ, D_ACT  ASC",
                       params)
        columns = [column[0] for column in cursor.description]
        results = 0
        rows = cursor.fetchall()
        for row in rows:
            d = dict(zip(columns, row))
            results += d["V_POIDS_CAPT"]
        return results       

    def list_all_activities(self):
        """
        Liste les activités présentes dans la base
        :param self: une session sur la base
        :return: une liste des activités
        """
        cursor = self.connection.cursor()
        cursor.execute("select * from ACTIVITE ORDER BY C_BAT, D_DBQ, D_ACT  ASC")
        columns = [column[0] for column in cursor.description]
        results = []
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(zip(columns, row)))
        return results


        # for row in cursor.columns(table='MAREE'):
        #     print("Field name: " + str(row.column_name))
        #     print("Type: " + str(row.type_name))
        #     print("Width: " + str(row.column_size))

    def get_operation_label(self, c_opera):
        """Retourne le nom de l'opération associé au code
        
        Arguments:
            c_opera {int} -- le code de l'opération
        
        Returns:
            string -- le nom de l'opération associé au code
        """
        params = [str(c_opera)]        
        cursor = self.connection.cursor()
        cursor.execute("select L_OPERA from OPERA WHERE C_OPERA= ? ",
                       params)
        return cursor.fetchone()[0]

    def get_specie_label(self, specie):
        """Retourne le nom de l'espèce associé au code
        
        Arguments:
            specie {int} -- le code de l'espece
        
        Returns:
            string -- le nom de l'espece associé au code
        """
        params = [str(specie)]        
        cursor = self.connection.cursor()
        cursor.execute("select C_ESP_3L from ESPECE WHERE C_ESP= ? ",
                       params)
        return cursor.fetchone()[0]        


def compare_data_test():
    """

    :return:
    """
    dataFileClassic = "France_OA_427_FLUX_AVDTH_1216_0117.mdb"
    dataFileERS = "AVDTH_20170124152723.mdb"

    databaseFileClassic = os.getcwd() + "\\" + dataFileClassic
    databaseFileERS = os.getcwd() + "\\" + dataFileERS

    # compare_data(databaseFileClassic, databaseFileERS)
    avdth_classic = AVDTH(databaseFileClassic)
    avdth_ers = AVDTH(databaseFileERS)
    print("Base de donnée: DB 1")
    avdth_classic.count_trip()
    avdth_classic.list_all_trips()
    avdth_classic.list_all_activities()

    print(avdth_classic.find_trip("FRA000724048-20160003"))

    # print("Base de donnée: DB 2")
    # avdth_ers.count_trip()
    # avdth_ers.list_all_trips()
    # avdth_ers.list_all_activities()


def compare_data(databasefile1, databasefile2):
    """

    :param databasefile1:
    :param databasefile2:
    :return:
    """
    avdth_db1 = AVDTH(databasefile1)
    avdth_ers = AVDTH(databasefile2)
    print("Base de donnée: DB 1")
    avdth_db1.count_trip()
    avdth_db1.list_all_trips()
    avdth_db1.list_all_activities()
    print("Base de donnée: DB 2")
    avdth_ers.count_trip()
    avdth_ers.list_all_trips()
    avdth_ers.list_all_activities()


def main(argv):
    databasefile1 = None
    databasefile2 = None
    try:
        opts, args = getopt.getopt(argv, "hi1:i2:", ["i1file=", "o2file="])
    except getopt.GetoptError:
        print('logbookcontrol.py -i1 <databasefile1> -i2 <databasefile2>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('logbookcontrol.py -i1 <databasefile1> -i2 <databasefile2>')
            sys.exit()
        elif opt in ("-i1", "--i1file"):
            databasefile = arg
        elif opt in ("-i2", "--i2file"):
            outputfile = arg
    if (databasefile1 == None and databasefile2 == None):
        compare_data_test()
        sys.exit()
    if (databasefile1 == None or databasefile2 == None):
        print('All databases files are mandatory (format CSV from the CNSP). See help below.')
        print('logbookcontrol.py -i1 <databasefile1> -i2 <databasefile2>')
        sys.exit(2)
    compare_data(databasefile1, databasefile2)


if __name__ == "__main__":
    main(sys.argv[1:])
