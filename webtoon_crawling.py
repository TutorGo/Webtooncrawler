import re
import sys
import os
from bs4 import BeautifulSoup
import requests
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFileDialog, QPushButton, QLineEdit, QVBoxLayout, \
    QVBoxLayout, QGridLayout, QMessageBox, QListWidget


class Webtooncrawler(QWidget):
    base_url = ''
    search_url = 'http://comic.naver.com/search.nhn'
    webtoon = []

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

        grid.addWidget(search_webtoon_label, 2, 0)
        grid.addWidget(self.search_webtoon_input, 2, 1)
        grid.addWidget(self.search_webtoon_input_button, 2, 2)

        # 웹툰 검색 리스트 레이아웃 설정
        search_webtoon_list_label = QLabel("Webtoon list", self)
        self.search_webtoon_list = QListWidget()
        self.search_webtoon_list_select_button = QPushButton('select', self)

        grid.addWidget(search_webtoon_list_label, 3, 0)
        grid.addWidget(self.search_webtoon_list, 3, 1)
        grid.addWidget(self.search_webtoon_list_select_button, 3, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 540, 300)
        self.show()

    def download_folder_path_select(self):
        if self.download_folder_path_set_text.text() == '':
            download_folder_path = QFileDialog.getExistingDirectory(directory='..')
            self.download_folder_path_set_text.setText(download_folder_path)
        try:
            os.chdir(self.download_folder_path_set_text.text())
        except FileNotFoundError as e:
            QMessageBox.about(self, '', '파일경로가 존재하지 않습니다 다시 설정해주세요')

    def search_webtoon(self):
        if self.download_folder_path_set_text.text() == '' or self.search_webtoon_input.text() == '':
            QMessageBox.about(self, '', 'download folder path or search input are empty')
        else:
            params = {"keyword": self.search_webtoon_input.text()}
            search_requests = requests.get(self.search_url, params)
            soup = BeautifulSoup(search_requests.text, 'lxml')
            webtoon_search_tag_resultBox = soup.select_one('div.resultBox')
            webtoon_search_tag_a_list = webtoon_search_tag_resultBox.select('ul.resultList > li > h5 > a')
            webtoon_search_tag_a_range = range(1, len(webtoon_search_tag_a_list) + 1)
            webtoon_titleId_pattenr = re.compile(r'.*[?]titleId=(\d+).*')
            self.search_webtoon_list.clear()
            if webtoon_search_tag_a_list == []:
                self.search_webtoon_list.addItem("검색결과가 없습니다")
            for index, webtoon_search_tag_a in zip(webtoon_search_tag_a_range, webtoon_search_tag_a_list):
                m = re.search(webtoon_titleId_pattenr, str(webtoon_search_tag_a))
                self.webtoon.append((index,webtoon_search_tag_a.get_text(),m.group(1)))
                self.search_webtoon_list.addItem('{}. {}'.format(index, webtoon_search_tag_a.get_text()))
                print(self.webtoon)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Webtooncrawler()
    sys.exit(app.exec_())
