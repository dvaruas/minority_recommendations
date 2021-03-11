import os
import sqlite3

SQL_FILE_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "data", "all_data.db")


class Manager:
    def __init__(self, name):
        self.db = sqlite3.connect(SQL_FILE_PATH)
        self.conn = self.db.cursor()
        self.table_name = name
        self.fields = {}

    def add_field(self, field_name, field_type):
        self.fields[field_name] = field_type

    def create_table(self):
        columns = []
        for field_name, field_type in self.fields.items():
            if field_type == "string":
                field_type = "TEXT"
            elif field_type == "int":
                field_type = "INTEGER"
            elif field_type == "float":
                field_type = "REAL"
            columns.append(f"{field_name} {field_type}")
        self.conn.execute("create table if not exists {} ({})".format(self.table_name, ",".join(columns)))

    def fetch(self, values):
        where_clauses = []
        for field_name, field_value in values.items():
            if field_name not in self.fields:
                continue
            if self.fields[field_name] == "string":
                field_value = f"'{field_value}'"
            where_clauses.append(f"{field_name}={field_value}")
        self.conn.execute("select {} from {} where {}".format(",".join(sorted(self.fields.keys())),
            self.table_name, " and ".join(where_clauses)))
        answers = []
        for row in self.conn:
            val_dict = {}
            for name, val in zip(sorted(self.fields.keys()), row):
                if self.fields[name] == "int":
                    val_dict[name] = int(val)
                elif self.fields[name] == "float":
                    val_dict[name] = float(val)
                else:
                    val_dict[name] = val
            answers.append(val_dict)
        return answers

    def insert(self, values, defer_commit=False):
        if self.fetch(values=values):
            return
        field_names = []
        field_values = []
        for field_name, field_value in values.items():
            if field_name not in self.fields:
                continue
            if self.fields[field_name] == "string":
                field_value = f"'{field_value}'"
            else:
                field_value = str(field_value)
            field_names.append(field_name)
            field_values.append(field_value)
        self.conn.execute("insert into {}({}) values ({})".format(self.table_name,
            ",".join(field_names), ",".join(field_values)))
        if not defer_commit:
            self.db.commit()

    def delete(self, values, defer_commit=False):
        where_clauses = []
        for field_name, field_value in values.items():
            if field_name not in self.fields:
                continue
            if self.fields[field_name] == "string":
                field_value = f"'{field_value}'"
            where_clauses.append(f"{field_name}={field_value}")
        self.conn.execute("delete from {} where {}".format(self.table_name, " and ".join(where_clauses)))
        if not defer_commit:
            self.db.commit()

    def commit(self):
        self.db.commit()

    def __del__(self):
        self.conn.close()
