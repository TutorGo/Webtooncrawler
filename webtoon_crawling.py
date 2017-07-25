import re
import sys
import os
from bs4 import BeautifulSoup
import requests
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFileDialog, QPushButton, QLineEdit, QVBoxLayout, \
    QVBoxLayout, QGridLayout


class Webtooncrawler(QWidget):
    base_url = ''
    search_url = 'http://comic.naver.com/search.nhn'

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        grid = QGridLayout()

        # 다운로드 폴더 레이아웃 설정
        download_folder_label = QLabel('Download Folder', self)
        self.download_folder_path_set_text = QLineEdit(self)
        self.download_folder_path_input_button = QPushButton('select', self)
        self.download_folder_path_input_button.clicked.connect(self.download_folder_path_select)

        grid.addWidget(download_folder_label, 1, 0)
        grid.addWidget(self.download_folder_path_set_text, 1, 1)
        grid.addWidget(self.download_folder_path_input_button, 1, 2)

        # 웹툰 검색 레이아웃 설정
        search_webtoon_label = QLabel('Webtoon', self)
        self.search_webtoon_input = QLineEdit(self)
        self.search_webtoon_input_button = QPushButton('search', self)
        self.search_webtoon_input_button.clicked.connect(self.search_webtoon)

        grid.addWidget(search_webtoon_label,2,0)
        grid.addWidget(self.search_webtoon_input, 2, 1)
        grid.addWidget(self.search_webtoon_input_button, 2, 2)
        self.setLayout(grid)
        self.setGeometry(300, 300, 540, 300)
        self.show()

    def download_folder_path_select(self):
        download_folder_path = QFileDialog.getExistingDirectory()
        self.download_folder_path_set_text.setText(download_folder_path)
        os.chdir(download_folder_path)

    def search_webtoon(self):
        params = {"keyword":self.search_webtoon_input.text()}
        search_requests = requests.get(self.search_url, params)
        soup = BeautifulSoup(search_requests.text, 'lxml')
        print(soup)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Webtooncrawler()
    sys.exit(app.exec_())
