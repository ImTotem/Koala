"""프로그램 진입점"""
import sys
from pathlib import Path

if __name__ == '__main__':
    # 프로젝트 루트 경로 설정
    PROJECT_ROOT = (
        Path(sys.executable).parent
        if getattr(sys, 'frozen', False)  # 실행 파일로 빌드된 경우

        else Path(__file__).parent.parent  # 개발 중 실행하는 경우
    )

    # Python 패키지 경로 추가 (import를 위해)
    sys.path.append(str(PROJECT_ROOT))

    import app

    app.run()
