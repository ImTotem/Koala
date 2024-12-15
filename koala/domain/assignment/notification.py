from datetime import datetime, timedelta

from plyer import notification

def notify(courses, has_changes=False):
    if has_changes:
        notification.notify(
            title='과제알림',
            message='새로운 과제 내역이 업데이트 되었습니다.',
            app_name='Koala',
            timeout=5,  # seconds
        )

    today = datetime.now()
    for course in courses:
        for assignment in course.assignments:

            if assignment.end_date is None:
                continue

            if assignment.end_date - today < timedelta(days=2):
                # 아침 9시, 점심 1시, 저녁 8시
                if (today.hour in {9, 13, 20}) and today.minute <= 3:
                    notification.notify(
                        title='과제알림',
                        message='과제 마감 기한이 2일 이내입니다.',
                        app_name='Koala',
                        timeout=5,  # seconds
                    )
