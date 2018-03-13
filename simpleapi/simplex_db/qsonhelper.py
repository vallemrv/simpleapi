# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   16-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: controllers.py
# @Last modified by:   valle
# @Last modified time: 10-Mar-2018
# @License: Apache license vesion 2.0

import os
import importlib
from django.forms.models import model_to_dict
from django.core import serializers
from django.conf import settings
from tokenapi.http import JsonError
from django.http import Http404
from .models import Model

class HelperBase(object):
    def __init__(self, JSONQuery, JSONResult):
        self.JSONResult = JSONResult
        self.JSONQuery = JSONQuery
        self.db = JSONQuery.get("db")
        self.rows = JSONQuery.get("rows")
        self.tipo = None
        for row in self.rows:
            self.action(row)

    def get_class(self, name):
        modulo = importlib.import_module(self.db+".models")
        try:
            return getattr(modulo, name)
        except AttributeError as a:
            print(str(a))
            return None

    def execute_filter(self, name, filter):
        class_model = self.get_class(name)
        return class_model.objects.filter(**filter)


    def get_rows(self, qson):
        rows = self.execute_filter(qson['db_table'], qson['filter'])
        if len(qson["exclude"]) > 0:
            for ex in qson["exclude"]:
                rows = rows.exclude(**ex)
        return rows


class AddHelper(HelperBase):

    def action(self, qson):
        if not 'add' in self.JSONResult:
            self.JSONResult["add"] = {}
        tb = qson["db_table"].lower()
        if tb not in self.JSONResult["add"]:
            self.JSONResult["add"][tb] = []
        row = self.modify_row(qson)
        if row != None:
            row.save()
            row_send = Model.model_to_dict(row)
            self.JSONResult['add'][tb].append(row_send)
            for qson_child in qson["childs"]:
                row_child = self.modify_row(qson_child)
                tb = qson_child["db_table"].lower()
                if tb not in self.JSONResult["add"]:
                    self.JSONResult["add"][tb] = []
                tb = qson_child["db_table"].lower()
                Model.child_add(qson_child, row, row_child)
                row_send = Model.model_to_dict(row_child)
                self.JSONResult['add'][tb].append(row_send)

    def modify_row(self, qson):
        class_model = self.get_class(qson["db_table"])
        if class_model != None:
            reg = qson["reg"]
            if 'id' in reg:
                try:
                    row = class_model.objects.get(pk=reg["id"])
                    for k, v in reg.items():
                        setattr(row, k, v)
                except:
                    row = class_model(**reg)
            else:
                row = class_model(**reg)

            return row
        else:
            return None

class GetHelper(HelperBase):

    def action(self, qson):
        tb = qson["db_table"].lower()
        rows = []
        if not 'get' in self.JSONResult:
            self.JSONResult["get"] = {}
        result = self.JSONResult["get"]
        if tb not in result:
            result[tb] = []

        rows = self.get_rows(qson)
        for row in rows:
            row_send = Model.model_to_dict(row)
            self.read_child(row, qson["childs"], row_send)
            result[tb].append(row_send)



    def read_child(self, row, childs, row_send):
        for child in childs:
            field = child["relation_field"]
            row_send[field] = []
            rows_child = Model.get(row, field, child["filter"], child["exclude"])
            for row_child in rows_child:
                row_send_child = Model.model_to_dict(row_child)
                row_send[field].append(row_send_child)
                self.read_child(row_child, child["childs"], row_send_child)




class RmHelper(HelperBase):

    def action(self, qson):
        tb = qson["db_table"].lower()
        rows = []
        if not 'rm' in self.JSONResult:
            self.JSONResult["rm"] = {}
        result = self.JSONResult["rm"]
        if tb not in result:
            result[tb] = []

        rows = self.get_rows(qson)
        if len(qson["childs"]) <= 0:
            row_send = Model.model_to_dict(row, "id")
            row_send['rows_delete':  len(rows)]
            result[tb] = row_send
            self.delete_rows(rows)
        else:
            for row in rows:
                row_send = Model.model_to_dict(row, "id")
                for child in qson["childs"]:
                    field = child["relation_field"]
                    row_send[field] = {'rows_delete': Model.delete(row, field, child["filter"], child["exclude"])}
                result[tb].append(row_send)

    def delete_rows(self, rows):
        for row in rows:
            row.delete();

class JoinHelper(HelperBase):

    def action(self, qson):
        tb = qson["db_table"].lower()
        rows = []
        if not 'join' in self.JSONResult:
            self.JSONResult["join"] = {}
        result = self.JSONResult["join"]
        if tb not in result:
            result[tb] = []

        rows = self.get_rows(qson)
        if len(qson["childs"]) <= 0:
            row_send = Model.model_to_dict(row, "id")
            row_send['rows_joined':  0]
            result[tb] = row_send
        else:
            for row in rows:
                row_send = Model.model_to_dict(row, "id")
                for child in qson["childs"]:
                    field = child["relation_field"]
                    row_send[field] = {'rows_joined': Model.join(row, field, child["filter"], child["exclude"])}
                result[tb].append(row_send)



class QSonHelper(object):
    def __init__(self):
        self.JSONResult = {}

    def decode_qson(self, qson):
        for name in qson.keys():
            if "add" == name:
                QSONRequire = qson.get("add")
                AddHelper(JSONQuery=QSONRequire,
                          JSONResult=self.JSONResult)

            if "get" == name:
                QSONRequire = qson.get("get")
                GetHelper(JSONQuery=QSONRequire,
                              JSONResult=self.JSONResult)

            if "rm" == name:
                QSONRequire = qson.get("rm")
                RmHelper(JSONQuery=QSONRequire,
                        JSONResult=self.JSONResult)

            if "join" == name:
                QSONRequire = qson.get("join")
                JoinHelper(JSONQuery=QSONRequire,
                        JSONResult=self.JSONResult)

        return self.JSONResult
