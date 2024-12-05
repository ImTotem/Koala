from datetime import datetime
from typing import Set
from urllib.parse import parse_qs, urlparse

import aiohttp
from bs4 import BeautifulSoup, Tag

from koala.domain.assignment.model import Course, AssignAssignment, QuizAssignment, VideoAssignment, Status
from koala.domain.auth.model import Cookies
from koala.utils import Subject


class AssignmentService(Subject):

    def __init__(self, cookies: Cookies, courses: Set[Course]):
        super().__init__()
        self._cookies = cookies
        self._courses = courses

    def get_assignments(self):
        assignments = []

        for course in self._courses:
            assignments.extend(course.assignments.values())

        return assignments

    async def crawling_course(self) -> None:
        """과정 목록 크롤링"""
        async with aiohttp.ClientSession(cookies=self._cookies) as session:
            async with session.get("https://el2.koreatech.ac.kr/") as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'lxml')
        course_tags = soup.select('table[x-show="tab==0"] tbody tr')

        for course_tag in course_tags:
            a_tag = course_tag.select_one('td > a')
            url = a_tag.get('href')
            name = a_tag.text.strip()
            _id = int(parse_qs(urlparse(url).query)['id'][0])

            self._courses.add(Course(_id, url, name))

    async def crawling_assignments(self, course: Course) -> bool:
        async with aiohttp.ClientSession(cookies=self._cookies) as session:
            async with session.get(f'{course.url}&section=0') as response:
                html = await response.text()

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

        # 과제 업데이트 및 변경 여부 반환
        has_changes = course.update(assignments)
        if has_changes:
            self.notify()
        return has_changes

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
