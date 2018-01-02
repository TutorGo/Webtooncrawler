import re
import sys
import os
import multiprocessing
from bs4 import BeautifulSoup
import requests
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFileDialog, QPushButton, QLineEdit, \
     QGridLayout, QMessageBox, QListWidget, QHBoxLayout, QProgressBar
import time
from PIL import Image


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
        # grid 반응형 레이아웃 설정
        grid = QGridLayout()

        # 다운로드 폴더 라벨 설정
        download_folder_label = QLabel('Download Folder')
        # 다운로드 폴더 경로 입력 라인
        self.download_folder_path_set_text = QLineEdit()
        # 다운로드 폴더 선택하는 버튼 설정
        self.download_folder_path_input_button = QPushButton('select')
        # 버튼 클릭시 download_folder_path_select 함수 실행
        self.download_folder_path_input_button.clicked.connect(self.download_folder_path_select)

        # 그리드 레이아웃을 2차원 배열이라고 생각하고 각각 라벨, 텍스트, 버튼을 1행에 설정
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

        # QApplication은 멀티프로세싱 상태 즉 메인이 아닐때는 동작을 안함
        # 그래서 로딩bar구현은 멀티프로세싱 상태에서는 전혀 다르게 구현해야 될거라 생각
        # self.loading_bar = QProgressBar()
        # grid.addWidget(self.loading_bar, 6, 0, 2, 3)

        self.download_button = QPushButton('download', self)
        grid.addWidget(self.download_button, 8, 1)
        self.download_button.clicked.connect(self.webtoon_images_download)

        self.setLayout(grid)
        self.setGeometry(300, 300, 540, 300)
        self.show()

    def OFALLwebtoonlist_selcet_webtoon(self):
        # webtoon list에서 선택한 웹툰
        select_webtoon_list = self.search_webtoon_list.selectedIndexes()
        # 선택한 웹툰의 번호를 들고옴
        select_webtoon_index = select_webtoon_list[0].row()
        # 선택한 웹툰의 이름과 타이틀아이디를 self.webtoon_name, self.webtoon_titleId 에 설정
        for select_webtoon in self.webtoon:
            if select_webtoon[0] == select_webtoon_index + 1:
                self.webtoon_name = select_webtoon[1]
                self.webtoon_titleId = select_webtoon[2]
        self.latest_episode_set.setText(self.get_latest_webtoon_episode())
        self.loading_bar.setValue(0)

    def download_folder_path_select(self):
        if self.download_folder_path_set_text.text() == '':
            # 선택한 폴더 경로 받아옴
            download_folder_path = QFileDialog.getExistingDirectory(directory='..')
            # 다운로드 폴더 텍스트 인풋에 선택한 폴더 경로를 설정
            self.download_folder_path_set_text.setText(download_folder_path)
        try:
            # 경로로 웹툰을 다운 받을 폴더 설정
            os.chdir(self.download_folder_path_set_text.text())
        except FileNotFoundError as e:
            QMessageBox.about(self, '', '파일경로가 존재하지 않습니다 다시 설정해주세요')

    def get_image_tag_list(self, num):
        '''
        한 화의 모든 img 태그를 list로 반환하는 함수
        '''
        params = {'titleId': self.webtoon_titleId, 'no': num}
        requests_result = requests.get(self.detail_url, params)
        soup = BeautifulSoup(requests_result.text, 'lxml')
        div_wt_viewer = soup.select_one('div.wt_viewer')
        img_list = div_wt_viewer.select('img')
        return img_list

    def get_latest_webtoon_episode(self):
        '''
        가장 최근의 웹툰화를 가져오는 함수
        '''
        parmas = {"titleId": self.webtoon_titleId}
        requests_resultes = requests.get(self.webtoon_list_url, parmas)
        soup = BeautifulSoup(requests_resultes.text, 'lxml')
        tag_latest_td_title = soup.select_one('td.title')
        latest_webtoon_episode_pattern = re.compile(r'.*[;&]no=(\d+).*')
        # /webtoon/detail.nhn?titleId=20853&no=1124&weekday=tue 이런식으로 a 태그가 구성되어져 제일 위에 있는 a 태그를 가져옴
        # 패턴에 일치하는 것이 가장 최근화
        latest_webtoon_episode = re.search(latest_webtoon_episode_pattern, str(tag_latest_td_title))
        return latest_webtoon_episode.group(1)

    def search_webtoon(self):
        if self.download_folder_path_set_text.text() == '' or self.search_webtoon_input.text() == '':
            QMessageBox.about(self, '', '다운로드 폴더 입력창이 비었거 또는 웹툰 검색창에 검색할 웹툰을 입력해주세요.')
        else:
            # 웹툰 다운로드 로딩 bar를 초기화
            self.loading_bar.setValue(0)
            # keyword=웹툰이름 넣기 위한 파람
            params = {"keyword": self.search_webtoon_input.text()}
            search_requests = requests.get(self.search_url, params)
            soup = BeautifulSoup(search_requests.text, 'lxml')
            # 웹툰 리스트 선택
            webtoon_search_tag_resultBox = soup.select_one('div.resultBox')
            webtoon_search_tag_a_list = webtoon_search_tag_resultBox.select('ul.resultList > li > h5 > a')
            # 검색했을때 나오는 웹툰 수의 범위
            webtoon_search_tag_a_range = range(1, len(webtoon_search_tag_a_list) + 1)
            # 웹툰의 타이틀 아이디 패턴 네이버 웹툰은 titleId로 웹툰을 구분함
            webtoon_titleId_pattenr = re.compile(r'.*[?]titleId=(\d+).*')
            # 검색 하기 전 웹툰 리스트를 초기화
            self.search_webtoon_list.clear()
            if webtoon_search_tag_a_list == []:
                self.search_webtoon_list.addItem("검색결과가 없습니다")
            for index, webtoon_search_tag_a in zip(webtoon_search_tag_a_range, webtoon_search_tag_a_list):
                # 웹툰 타이틀아이디 검색
                webtoon_titleId = re.search(webtoon_titleId_pattenr, str(webtoon_search_tag_a))
                self.webtoon.append((index, webtoon_search_tag_a.get_text(), webtoon_titleId.group(1)))
                # search_webtoon_list에 검색한 웹툰 표시
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
        start_time = time.time()
        for index, episode in enumerate(episode_range):
            try:
                os.mkdir('{}화'.format(episode))
                os.rmdir('{}화'.format(episode))
            except FileExistsError:
                QMessageBox.about(self, '', '{}화가 이미 있습니다 폴더를 삭제하거나 다음화 부터 받아주세요'.format(episode))
            procs = []
            # python 멀티프로세싱을 이용해서 한 에피소드에 한개의 프로세스를 배정해서 동시에 다운로드
            p = multiprocessing.Process(target=self.process_image, args=(episode, headers))
            procs.append(p)
            p.start()
        for index, p in enumerate(procs):
            p.join()

        end_time = time.time() - start_time
        print(end_time)
        QApplication.alert(QMessageBox.about(self, 'Complete', '다운로드가 완료 되었습니다.'))
        os.chdir('..')

    def image_size_check(self, episode, image_link, headers):
        '''
        실제 웹툰 처럼 보여주기 위해서 중앙정렬을 하기위한 웹툰 이미지의 width를 구하는 함수
        <div style="width:{width}; margin:0 auto;"><img src={path}> 이렇게 width구해서 중앙 정렬을 한다
        '''
        response = requests.get(image_link['src'], headers=headers)
        with open('image{}.jpg'.format(episode), 'wb') as image:
            image.write(response.content)
        with Image.open('image{}.jpg'.format(episode)) as img:
            width, height = img.size
        os.remove('image{}.jpg'.format(episode))
        return width

    def process_image(self, episode, headers):

        img_list = self.get_image_tag_list(episode)
        image_size = self.image_size_check(episode, img_list[0], headers)
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
                    html.write('<div style="width:{width}; margin:0 auto;"><img src={path}> \n'.format(width=image_size,
                                                                                                       path=path))
            else:
                with open('{}화.html'.format(episode), 'a+') as html:
                    html.write('<img src={path}> \n'.format(path=path))
        if episode == 1:
            with open('{}화.html'.format(episode), 'a+') as html:
                html.write('<a href="{}화.html" style="float: right; font-size: 30px;">다음화</a></div>'.format(
                    episode + 1))
        else:
            with open('{}화.html'.format(episode), 'a+') as html:
                html.write('<a href="{}화.html" style="float: left; font-size: 30px;">이전화</a>\n \
                            <a href="{}화.html" style="float: right; font-size: 30px;">다음화</a></div>'.format(
                    episode - 1, episode + 1))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Webtooncrawler()
    sys.exit(app.exec_())
