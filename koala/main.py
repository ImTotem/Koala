"""프로그램 진입정

프로젝트 실행 루트를 설정
"""

import sys
from pathlib import Path

if __name__ == '__main__':
    # 프로젝트 루트 경로 설정
    PROJECT_ROOT = (
        Path(sys._MEIPASS)  # PyInstaller로 빌드된 경우
        if getattr(sys, 'frozen', False)
        else Path(__file__).parent.parent  # 개발 중 실행하는 경우
    )

    # Python 패키지 경로 추가
    sys.path.append(str(PROJECT_ROOT))

    from koala import app  # koala 패키지에서 직접 import
    app.run()
