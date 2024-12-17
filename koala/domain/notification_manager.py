from datetime import datetime, timedelta

from plyer import notification


class NotificationManager:
    """알림 관리자"""

    def __init__(self):
        # 이미 알림을 보낸 과제 ID 저장
        self._notified_assignments = set()

    def check_new_assignments(self, assignments: list):
        """새로운 과제 확인 및 알림 발송

        :param assignments: 현재 과제 목록
        :type assignments: list[Assignment]
        """
        assignments = set(assignments)
        if assignments - self._notified_assignments:
            self._send_new_assignment_notification()
            self._notified_assignments = assignments

        today = datetime.now()
        for assignment in assignments:

            if assignment.end_date is None:
                continue

            if assignment.end_date - today < timedelta(days=2):
                # 아침 9시, 점심 1시, 저녁 8시
                if (today.hour in {9, 13, 20}) and today.minute <= 3:
                    self._send_dday_notification()

    def _send_new_assignment_notification(self):
        """새로운 과제 알림 발송"""
        notification.notify(
            title='과제알림',
            message='새로운 과제 내역이 업데이트 되었습니다.',
            app_name='Koala',
            timeout=5,  # seconds
        )

    def _send_dday_notification(self):
        """과제 마감 알림 발송"""
        notification.notify(
            title='과제알림',
            message='과제 마감 기한이 2일 이내입니다.',
            app_name='Koala',
            timeout=5,  # seconds
        )

    def clear(self):
        """알림 이력 초기화"""
        self._notified_assignments.clear()
