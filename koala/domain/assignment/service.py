from datetime import datetime
from typing import Set
from requests.cookies import RequestsCookieJar
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from koala.domain.assignment.dto import AssignmentDTO
from koala.domain.assignment.model import Course, AssignAssignment, QuizAssignment, VideoAssignment, Status
from koala.utils import Subject


class AssignmentService(Subject):

    def __init__(self, cookies: RequestsCookieJar):
        super().__init__()
        self._cookies = cookies
        self._courses: Set[Course] = set()

    def get_assignments(self):
        assignments = []

        for course in self._courses:
            assignments.extend(course.assignments.values())

        return list(map(lambda x:AssignmentDTO.factory(x), assignments))

    def crawling_course(self):
        """과정 목록 크롤링"""
        print('[AssignmentService] Try Crawling Courses')

        with requests.Session() as session:
            session.cookies.update(self._cookies)

            response = session.get("https://el2.koreatech.ac.kr/")
            html = response.text

            soup = BeautifulSoup(html, 'lxml')
            course_tags = soup.select('table[x-show="tab==0"] tbody tr')

            for course_tag in course_tags:
                a_tag = course_tag.select_one('td > a')
                url = a_tag.get('href')
                name = a_tag.text.strip()
                _id = int(parse_qs(urlparse(url).query)['id'][0])

                self._courses.add(Course(_id, url, name))

        print('[AssignmentService] Crawling Courses Success')

    def crawling_assignments(self):
        with requests.Session() as session:
            session.cookies.update(self._cookies)

            for course in self._courses:
                print(f'[AssignmentService] Try Crawling Assignments - {course.name}')

                response = session.get(f'{course.url}&section=0')
                html = response.text

                soup = BeautifulSoup(html, 'lxml')
                assignment_tags = soup.select('li[class*="quiz"], li[class*="tubevod"], li[class*="assign"]')

                assignments = []
                for tag in assignment_tags:
                    classes = tag.get('class')
                    tag = tag.select('div > div > div')[1]
                    if 'assign' in classes:
                        assignments.append(self._crawling_assign(tag))
                    elif 'quiz' in classes:
                        assignments.append(self._crawling_quiz(tag))
                    elif 'tubevod' in classes:
                        assignment = self._crawling_video(tag)
                        if assignment:
                            assignments.append(assignment)

                course.update(assignments)

                print(f'[AssignmentService] Crawling Assignments Success - {course.name}')

        # 과제 업데이트 및 변경 여부 반환
        self.notify()

    def _crawling_assign(self, tag: Tag):
        activity, actions, *etc = tag.select('div')
        a_tag = activity.select_one('a')
        url = a_tag.get('href')
        _id = int(parse_qs(urlparse(url).query)['id'][0])

        title = a_tag.select_one('span').text.strip()

        status_tag = actions.select_one('strong')
        status = None
        if status_tag:
            status = status_tag.text.strip()
            status = Status.from_string(status)

        date_tag = activity.select_one('strong')
        start_date, end_date = None, None
        if date_tag:
            start_date, end_date = date_tag.text.strip().split(' ~ ')

            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M')

        return AssignAssignment(
            _id=_id,
            url=url,
            title=title,
            status=status,
            start_date=start_date,
            end_date=end_date
        )

    def _crawling_quiz(self, tag: Tag):
        activity, actions, *etc = tag.select('div')
        a_tag = activity.select_one('a')
        url = a_tag.get('href')
        _id = int(parse_qs(urlparse(url).query)['id'][0])

        title = a_tag.select_one('span').text.strip()

        status_tag = actions.select_one('strong')
        status = None
        if status_tag:
            status = status_tag.text.strip()
            status = Status.from_string(status)

        date_tag = activity.select_one('strong')
        start_date, end_date = None, None
        if date_tag:
            start_date, end_date = date_tag.text.strip().split(' ~ ')

            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M')

        return QuizAssignment(
            _id=_id,
            url=url,
            title=title,
            status=status,
            start_date=start_date,
            end_date=end_date
        )

    def _crawling_video(self, tag: Tag):
        activity, actions, *etc = tag.select('div')
        a_tag = activity.select_one('a')
        url = a_tag.get('href')
        _id = int(parse_qs(urlparse(url).query)['id'][0])

        title = a_tag.select_one('span').text.strip()

        status, *progress = actions.select('div > strong')
        status = Status.from_string(status.text.strip())
        if status == Status.비활성:
            return None

        progress = int(progress[0].select_one('em').text.strip())
        date_tag = activity.select_one('strong')
        start_date, end_date = None, None
        if date_tag:
            start_date, end_date = date_tag.text.strip().split(' ~ ')

            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M')

        return VideoAssignment(
            _id=_id,
            url=url,
            title=title,
            status=status,
            start_date=start_date,
            end_date=end_date,
            progress=progress
        )


__all__ = (
    'AssignmentService',
)
