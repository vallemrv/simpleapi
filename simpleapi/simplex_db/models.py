# @Author: Manuel Rodriguez <valle>
# @Date:   07-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 16-Mar-2018
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
            try:
                getattr(row, field).add(row_child, bulk=False)
            except TypeError:
                getattr(row, field).add(row_child)




    @staticmethod
    def get(row, field, filter, exclude):
        if hasattr(row, field+"_set"):
            rows = getattr(row, field+"_set").filter(**filter)
            for ex in exclude:
                rows = rows.exclude(**ex)
        else:
            rows  = getattr(row, field).filter(**filter)
            for ex in exclude:
                rows = rows.exclude(**ex)
        return rows

    @staticmethod
    def delete(row, field, filter, exclude):
        if hasattr(row, field+"_set"):
            rows = getattr(row, field+"_set").filter(**filter)
            for ex in exclude:
                rows = rows.exclude(**ex)
            count = len(rows)
            getattr(row, field+"_set").remove(*rows)

        else:
            rows  = getattr(row, field).filter(**filter)
            for ex in exclude:
                rows = rows.exclude(**ex)
            count = len(rows)
            getattr(row, field).remove(*rows)

        return count

    @staticmethod
    def join(row, field, filter, exclude):
        if hasattr(row, field+"_set"):
            rows = getattr(row, field+"_set").filter(**filter)
            for ex in exclude:
                rows = rows.exclude(**ex)
            count = len(rows)
            try:
                getattr(row, field+"_set").add(*rows, bulk=False)
            except TypeError:
                getattr(row, field+"_set").add(*rows)


        else:
            rows  = getattr(row, field).filter(**filter)
            for ex in exclude:
                rows = rows.exclude(**ex)
            count = len(rows)
            try:
                getattr(row, field).add(*rows, bulk=False)
            except TypeError:
                getattr(row, field).add(*rows)


        return count


    @staticmethod
    def toArrayDict(regs, *columns):
        lista = []
        for r in regs:
            reg = Model.model_to_dict(r, *columns)
            lista.append(reg)

        return lista

    @staticmethod
    def model_to_dict(model, *columns):
        dict_resul = {}
        for k, v in model.__dict__.items():
            if len(columns) == 0 or k in columns:
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
