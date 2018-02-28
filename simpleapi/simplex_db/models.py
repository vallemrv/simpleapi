# @Author: Manuel Rodriguez <valle>
# @Date:   07-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 23-Feb-2018
# @License: Apache license vesion 2.0

import sqlite3
import decimal
import datetime

class Model(object):

    @staticmethod
    def exitsTable(db_name, table_name):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
        sql = sql % table_name
        db = sqlite3.connect(db_name)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        return reg != None


    @staticmethod
    def child_add(qson_child, row, row_child):
        field = qson_child["relation_field"]
        if hasattr(row, field+"_set"):
            try:
                getattr(row, field+"_set").add(row_child, bulk=False)
            except TypeError:
                getattr(row, field+"_set").add(row_child)
        else:
            row_child.save()
            try:
                getattr(row, field).add(row_child, bulk=False)
            except TypeError:
                getattr(row, field).add(row_child)




    @staticmethod
    def get(row, field, filter, exclude):
        if hasattr(row, field+"_set"):
            rows = getattr(row, field+"_set").filter(**filter).exclude(**exclude)
        else:
            rows  = getattr(row, field).filter(**filter).exclude(**exclude)
        return rows

    @staticmethod
    def delete(row, field,  filter):
        if hasattr(row, field+"_set"):
            rows = getattr(row, field+"_set").filter(**filter["filter"]).exclude(**filter["exclude"])
            count = len(rows)
            for r in rows:
                getattr(row, field+"_set").remove(r)

        else:
            rows  = getattr(row, field).filter(**filter["filter"]).exclude(**filter["exclude"])
            count = len(rows)
            for r in rows:
                getattr(row, field).remove(r)

        return count


    @staticmethod
    def toArrayDict(regs, columns="*"):
        lista = []
        for r in regs:
            reg = Model.model_to_dict(r, columns=columns)
            lista.append(reg)

        return lista

    @staticmethod
    def model_to_dict(model, columns="*"):
        dict_resul = {}
        for k, v in model.__dict__.items():
            if type(v) in (str, unicode, bool, int, float, long,
                           decimal.Decimal, datetime.datetime, datetime.date):
                dict_resul[k] = v
        return dict_resul

    @staticmethod
    def deleteChidls(regs):
        lista = []
        for r in regs:
            reg = Model.model_to_dict(r, columns=columns)
            lista.append(reg)
            r.delete()

        return lista
