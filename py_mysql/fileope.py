#-------------------------------------------------------------------------------
# Name:        fileope.py
# Purpose:     ファイル操作用モジュール
#
# Author:      shikano.takeki
#
# Created:     22/12/2017
# Copyright:   (c) shikano.takeki 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import os


def get_file_names(self, dir_path: str):
    """指定したディレクトリ直下のファイル名一覧を取得する関数,

    Args:
        param1 dir_path: ファイル名一覧を取得するディレクトリパス.

    Returns:
        ファイル名の一覧を格納したリスト.
    """
    file_names = list()
    for file in os.listdir(dir_path):
        if os.path.isfile(dir_path + file):
            file_names.append(file)

    return file_names

def main():
    pass

if __name__ == '__main__':
    main()
