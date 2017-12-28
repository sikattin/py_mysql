#-------------------------------------------------------------------------------
# Name:        muysql_custom.py
# Purpose:     MySQL謹製のmysql-connector-pythonのラッパークラス
# を実装したモジュール.
#
# Author:      shikano.takeki
#
# Created:     08/12/2017
# Copyright:   shikano.takeki 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import mysql.connector
from py_mysql.delete_null_row import DeleteNullRow
from getpass import getpass


class MySQLDB(object):
    """MySQL謹製のmysql-connector-pythonのラッパークラス"""
    def __init__(self, host:str, dst_db: str, myuser: str, mypass: str, port: int):
        """コンストラクタ.

        各種初期化を行う.
        :param host: データベースの接続ホスト.
        :param dst_db: 接続先のデータベース名.
        :param myuser: 接続するユーザー名.
        :param mypass: 接続するユーザのパスワード.
        """
        self.dnr = DeleteNullRow()
        self.host = host
        self.dst_db = dst_db
        self.myuser = myuser
        self.mypass = mypass
        self.port = port
        self._conn = None
        self._cur = None
        self._autocommit = False

        # 初期化時にDBに接続する.
        self.connect(self.host, self.dst_db, self.myuser, self.mypass, self.port)

    def __enter__(self):
        """コンテキストマネージャ実装のため."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャ実装のため.

        :param exc_type:
        :param exc_val:
        :param exc_val:
        :param exc_tb:
        """
        self.close()
        if not self.is_connect:
            print("DB接続をクローズしました。")

    def connect(self, host: str, dest_db: str, myuser: str, mypass: str, port:int):
        """MySQL接続用関数.

        """
        try:
            self._conn = mysql.connector.connect(user=self.myuser,
                password=self.mypass,
                database=self.dst_db,
                host=self.host,
                port=self.port)
        except mysql.connector.errors.ProgrammingError as e1:
            print("正確なアカウント情報、DB名を指定してください。")
            hostname = input("hostname: ")
            username = input("user: ")
            password = getpass()
            database = input("destination_db: ")
            port_num = input("Port: ")
            self._conn = mysql.connector.connect(user=username,
                    password=password,
                    database=database,
                    host=hostname,
                    port=port_num)
            if self._conn.is_connected():
                self._cur = self._conn.cursor(buffered=True)
                self.autocommit_on()
                return self
        else:
            if self._conn.is_connected():
                print("DB名：{} への接続成功.".format(self.dst_db))
                # カーソルの取得
                self._cur = self._conn.cursor(buffered=True)
                self.autocommit_on()
                return self

    def close(self):
        """接続しているデータベースのクローズを行う."""
        if self._conn.is_connected():
            self._cur.close()
            self._conn.close()
            self._conn = None
            self._cur = None

    def commit(self):
        """接続しているデータベースへのコミットを行う."""
        self._conn.commit()
        print("これまでの更新をコミットしました。\n")

    def rollback(self):
        """トランザクション処理をロールバックする."""
        self._conn.rollback()
        print("ロールバックしました。\n")

    def fetchone(self):
        """カーソルから次の1レコードを取得する.

        Returns a tuple or None.
        """
        return self._cur.fetchone()

    def fetchall(self):
        """カーソルから全レコードを取得する.

        Returns a list of tuples.
        """
        return self._cur.fetchall()

    def is_connect(self) -> bool:
        """データベースへの接続状況を教えてくれる."""
        return self._conn.is_connected()

    def get_cursor(self):
        """カーソルを取得する."""
        return self._cur

    def change_database(self, db: str):
        """接続先のデータベースを変更する."""
        self._conn.database = db

    def get_statement(self):
        """returns the last executed statement as a string."""
        return self._cur.statement

    def autocommit_on(self):
        """autocommitをONにセットする."""
        self._conn.autocommit = True
        self._autocommit = self._conn.autocommit
        self._cur = self._conn.cursor(buffered=True)
        return print("autocommit = {}".format(self._autocommit))

    def autocommit_off(self):
        """autocommitをOFFにセットする."""
        self._conn.autocommit = False
        self._autocommit = self._conn.autocommit
        self._cur = self._conn.cursor(buffered=True)
        return print("autocommit = {}".format(self._autocommit))

    def get_autocommit(self):
        """return autocommit value."""
        return self._autocommit

    def execute_sql(self, sql: str, params=None):
        """SQL文の実行をする.

        :param sql: 実行するクエリ、コマンド
        :param params: 割り当て用のパラメータ 要タプル型"""
        # 接続確認
        if not self.is_connect:
            self.connect(self.host, self.dst_db, self.myuser, self.mypass, self.port)
        try:
            cur = self.get_cursor()
            if params is None:
                self._cur.execute(sql)
            else:
                # パラメータがタプル型かどうかを検査する.
                # タプル型でなかった場合例外を発生させる.
                if not isinstance(params, tuple):
                    params = tuple(params)
                    if not isinstance(params, tuple):
                        raise ValueError("割り当てパラメータはタプル型でなければなりません。")
                self._cur.execute(sql)
        except mysql.connector.Error as e:
            raise e
        else:
            return self._cur

    def execute_sqls(self):
        """複数のSQL文を実行する."""

    def is_transacted(self) -> bool:
        """トランザクションの状態を取得する.

        トランザクション処理中ならばTrueを返す.
        """
        return self._conn.in_transaction

    def escape_statement(self, sql: str):
        """引数で渡された文字列をエスケープして返す.

            Args:
                param1 sql: execution command.

            Returns:
                String escaped.
        """
        # 新しいリストを用意.
        list_escaped = list()
        # 文字列を単語単位で区切る.
        split_statement = sql.split()
        # シングルクォーテーションまたはダブルクォーテーションではじまる
        # ワードの場合のみエスケープ処理を施す
        for word in split_statement:
            search_objs = ["^'.+'$", '^".+"$']
            if self.dnr.is_matched(line=word, search_objs=search_objs):
                word = self.escape(word[1:-1])
                word = "'" + word + "'"
            list_escaped.append(word)
        # 最後に1つの文字列に連結してリターン.
        return ' '.join(list_escaped)

    def escape(self, value: str):
        """SQLステートメントのパラメータ部分のエスケープをする.

        Args:
            param1 value: エスケープ対象の文字列.

        Returns:
            エスケープ後の文字列.
        """
        if value is None:
            return value
        if isinstance(value, (bytes, bytearray)):
            value = value.replace(b'\\', b'\\\\')
            value = value.replace(b'\n', b'\\n')
            value = value.replace(b'\r', b'\\r')
            value = value.replace(b'\047', b'\134\047')  # single quotes
            value = value.replace(b'\042', b'\134\042')  # double quotes
            value = value.replace(b'\032', b'\134\032')  # for Win32
        else:
            value = value.replace('\\', '\\\\')
            value = value.replace('\n', '\\n')
            value = value.replace('\r', '\\r')
            value = value.replace('\047', '\134\047')  # single quotes
            value = value.replace('\042', '\134\042')  # double quotes
            value = value.replace('\032', '\134\032')  # for Win32
        return value

    def get_dbtable(self):
        """データベース名とテーブル名の一覧を取得する.

            Returns:
                データベース名とテーブル名を対応させた辞書.
                {'db1': (db1_table1, db1_table2, ...), 'db2': (db2_table1, ...)}
        """
        results = {}
        # SHOW DATABASES;
        sql = self.escape_statement("SHOW DATABASES;")
        cur_showdb = self.execute_sql(sql)
        for db_name in cur_showdb.fetchall():
            for db_str in db_name:
                # information_schema と peformance_schema DBはバックアップ対象から除外.
                if db_str.lower() in {'information_schema', 'performance_schema'}:
                    continue
                # DBに接続する.
                self.change_database(db_str)
                # SHOW TABLES;
                sql = self.escape_statement("SHOW TABLES;")
                cur_showtb = self.execute_sql(sql)
                for table_name in cur_showtb.fetchall():
                    for table_str in table_name:
                        # 辞書にキーとバリューの追加.
                        results.setdefault(db_str, []).append(table_str)
        return results
