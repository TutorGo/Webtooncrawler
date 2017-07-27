import re
import sys
import os

from PyQt5.QtCore import QSize
from bs4 import BeautifulSoup
import requests
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFileDialog, QPushButton, QLineEdit, QVBoxLayout, \
    QVBoxLayout, QGridLayout, QMessageBox, QListWidget, QFrame, QHBoxLayout, QGroupBox, QFormLayout, QProgressBar


class Webtooncrawler(QWidget):
    detail_url = 'http://comic.naver.com/webtoon/detail.nhn?'
    webtoon_list_url = 'http://comic.naver.com/webtoon/list.nhn?'
    search_url = 'http://comic.naver.com/search.nhn'
    webtoon = []
    webtoon_titleId = ''
    webtoon_name = ''

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()

        download_folder_label = QLabel('Download Folder')
        self.download_folder_path_set_text = QLineEdit()
        self.download_folder_path_input_button = QPushButton('select')
        self.download_folder_path_input_button.clicked.connect(self.download_folder_path_select)

        grid.addWidget(download_folder_label, 1, 0)
        grid.addWidget(self.download_folder_path_set_text, 1, 1)
        grid.addWidget(self.download_folder_path_input_button, 1, 2)

        # 웹툰 검색 레이아웃 설정
        search_webtoon_label = QLabel('Webtoon')
        self.search_webtoon_input = QLineEdit()
        self.search_webtoon_input_button = QPushButton('search')
        self.search_webtoon_input_button.clicked.connect(self.search_webtoon)

        grid.addWidget(search_webtoon_label, 2, 0)
        grid.addWidget(self.search_webtoon_input, 2, 1)
        grid.addWidget(self.search_webtoon_input_button, 2, 2)

        # 웹툰 검색 리스트 레이아웃 설정
        search_webtoon_list_label = QLabel("Webtoon list")
        self.search_webtoon_list = QListWidget()
        self.search_webtoon_list_select_button = QPushButton('select')
        self.search_webtoon_list_select_button.clicked.connect(self.OFALLwebtoonlist_selcet_webtoon)

        grid.addWidget(search_webtoon_list_label, 3, 0)
        grid.addWidget(self.search_webtoon_list, 3, 1)
        grid.addWidget(self.search_webtoon_list_select_button, 3, 2)

        self.latest_episode_layout = QHBoxLayout()
        self.latest_episode_set = QLineEdit()
        self.latest_episode_layout.addStretch()
        self.latest_episode_layout.addWidget(QLabel('latest episode'))
        self.latest_episode_layout.addWidget(self.latest_episode_set)
        self.latest_episode_set.setMaximumSize(40, 20)
        self.latest_episode_layout.addStretch()

        grid.addLayout(self.latest_episode_layout, 4, 1)

        self.episode_range_layout = QHBoxLayout()
        self.episode_range_layout.addStretch()
        self.episode_range_layout.addWidget(QLabel('episode'))
        self.episode_range_layout.addWidget(QLabel('min'))
        self.episdoe_min_range_input = QLineEdit()
        self.episdoe_min_range_input.setMaximumSize(40, 20)
        self.episode_range_layout.addWidget(self.episdoe_min_range_input)
        self.episode_range_layout.addWidget(QLabel('~'))
        self.episode_range_layout.addWidget(QLabel('max'))
        self.episdoe_max_range_input = QLineEdit()
        self.episdoe_max_range_input.setMaximumSize(40, 20)
        self.episode_range_layout.addWidget(self.episdoe_max_range_input)
        self.episode_range_layout.addStretch()

        grid.addLayout(self.episode_range_layout, 5, 1)

        self.loading_bar = QProgressBar()
        grid.addWidget(self.loading_bar, 6, 0, 2, 3)

        self.download_button = QPushButton('download', self)
        grid.addWidget(self.download_button, 8, 1)
        self.download_button.clicked.connect(self.webtoon_images_download)

        self.setLayout(grid)
        self.setGeometry(300, 300, 540, 300)
        self.show()

    def OFALLwebtoonlist_selcet_webtoon(self):
        select_webtoon_list = self.search_webtoon_list.selectedIndexes()
        select_webtoon_index = select_webtoon_list[0].row()
        for select_webtoon in self.webtoon:
            if select_webtoon[0] == select_webtoon_index + 1:
                self.webtoon_name = select_webtoon[1]
                self.webtoon_titleId = select_webtoon[2]
        self.latest_episode_set.setText(self.get_latest_webtoon_episode())
        self.loading_bar.setValue(0)


    def download_folder_path_select(self):
        if self.download_folder_path_set_text.text() == '':
            download_folder_path = QFileDialog.getExistingDirectory(directory='..')
            self.download_folder_path_set_text.setText(download_folder_path)
        try:
            os.chdir(self.download_folder_path_set_text.text())
        except FileNotFoundError as e:
            QMessageBox.about(self, '', '파일경로가 존재하지 않습니다 다시 설정해주세요')

    def get_image_tag_list(self, num):
        params = {'titleId': self.webtoon_titleId, 'no': num}
        requests_result = requests.get(self.detail_url, params)
        soup = BeautifulSoup(requests_result.text, 'lxml')
        div_wt_viewer = soup.select_one('div.wt_viewer')
        img_list = div_wt_viewer.select('img')
        return img_list

    def get_latest_webtoon_episode(self):
        parmas = {"titleId": self.webtoon_titleId}
        requests_resultes = requests.get(self.webtoon_list_url, parmas)
        soup = BeautifulSoup(requests_resultes.text, 'lxml')
        tag_latest_td_title = soup.select_one('td.title')
        latest_webtoon_episode_pattern = re.compile(r'.*[;&]no=(\d+).*')
        latest_webtoon_episode = re.search(latest_webtoon_episode_pattern, str(tag_latest_td_title))
        return latest_webtoon_episode.group(1)

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
                webtoon_titleId = re.search(webtoon_titleId_pattenr, str(webtoon_search_tag_a))
                self.webtoon.append((index, webtoon_search_tag_a.get_text(), webtoon_titleId.group(1)))
                self.search_webtoon_list.addItem('{}. {}'.format(index, webtoon_search_tag_a.get_text()))

    def webtoon_images_download(self):
        try:
            os.mkdir(self.webtoon_name)
            os.chdir(os.getcwd() + '/' + self.webtoon_name)
        except FileExistsError:
            os.chdir(os.getcwd() + '/' + self.webtoon_name)
        headers = {'Referer': 'https://www.naver.com/'}
        start = int(self.episdoe_min_range_input.text())
        end = int(self.episdoe_max_range_input.text()) + 1
        self.loading_bar.setRange(0, end - start)
        episode_range = range(start, end)
        for episode in episode_range:
            img_list = self.get_image_tag_list(episode)
            try:
                os.mkdir('{}화'.format(episode))
                for index, img in enumerate(img_list):
                    response = requests.get(img['src'], headers=headers)
                    os.chdir("{}화".format(episode))
                    with open('image{}.jpg'.format(index), 'wb') as image:
                        image.write(response.content)
                    path = "{}화/image{}.jpg".format(episode, index)
                    os.chdir('..')
                    if index == 0:
                        with open('{}화.html'.format(episode), 'a+') as html:
                            html.write('<div style="width:690; margin:0 auto;"><img src={path}> \n'.format(path=path))
                    else:
                        with open('{}화.html'.format(episode), 'a+') as html:
                            html.write('<img src={path}> \n'.format(path=path))
                QApplication.processEvents()
                self.loading_bar.setValue(episode)
                if episode == 1:
                    with open('{}화.html'.format(episode), 'a+') as html:
                        html.write('<a href="{}화.html" style="float: right; font-size: 30px;">다음화</a></div>'.format(episode + 1))
                else:
                    with open('{}화.html'.format(episode), 'a+') as html:
                        html.write('<a href="{}화.html" style="float: left; font-size: 30px;">이전화</a>\n \
                                    <a href="{}화.html" style="float: right; font-size: 30px;">다음화</a></div>'.format(episode - 1, episode + 1))
            except FileExistsError:
                QMessageBox.about(self,'','{}화가 이미 있습니다 폴더를 삭제하거나 다음화 부터 받아주세요'.format(episode))
        os.chdir('..')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Webtooncrawler()
    sys.exit(app.exec_())
