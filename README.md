YouTube Video Downloader
YouTube 동영상을 다운로드하고, 동영상 정보를 추출하며, 멤버십(회원 전용) 콘텐츠를 인증을 통해 처리하는 Python 스크립트입니다. 다운로드된 동영상은 youtube_video 폴더에 저장되며, 메타데이터는 CSV 파일로 내보낼 수 있습니다.
⚠️ 중요: 이 도구는 교육 목적으로만 사용해야 합니다. YouTube 이용약관을 준수하며, 허가받은 콘텐츠만 다운로드하세요. 멤버십 콘텐츠나 저작권이 있는 콘텐츠를 무단으로 다운로드하는 것은 법률 및 플랫폼 정책을 위반할 수 있습니다.
기능

동영상 다운로드: YouTube 동영상을 MP4 형식으로 youtube_video 폴더에 다운로드.
동영상 정보 추출: 제목, 채널, 조회수, 사용 가능한 포맷 등의 메타데이터를 추출하여 CSV로 저장.
멤버십 콘텐츠 처리: 쿠키 파일 또는 Selenium을 통한 수동 로그인을 통해 멤버십 전용 동영상에 접근.
외부 플레이어 재생: VLC와 같은 외부 플레이어로 동영상을 재생하거나, 직접 URL을 복사.
다양한 URL 지원: youtube.com, youtu.be, embed, shorts 등 다양한 YouTube URL 형식 지원.
진행 상황 표시: 다운로드 진행 상황을 tqdm 프로그레스 바로 시각화.

설치
요구사항

Python 3.6 이상
Chrome 브라우저 및 호환되는 ChromeDriver
필요한 Python 패키지:pip install yt-dlp selenium requests pandas tqdm pyperclip webdriver-manager



설치 단계

저장소를 클론합니다:
git clone https://github.com/your-username/youtube-video-downloader.git
cd youtube-video-downloader


가상 환경을 설정합니다 (선택 사항):
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows


필수 패키지를 설치합니다:
pip install -r requirements.txt

requirements.txt 예시:
yt-dlp
selenium
requests
pandas
tqdm
pyperclip
webdriver-manager


ChromeDriver를 자동으로 관리하려면 webdriver-manager를 사용하세요. 수동 설치가 필요하면 ChromeDriver를 다운로드하여 PATH에 추가하세요.


사용 방법
실행
python youtube_video_downloader.py

단계별 안내

옵션 선택:

1: 일반 동영상 다운로드 및 정보 추출.
2: 멤버십 전용 동영상 처리 (인증 필요).


쿠키 파일 입력 (선택):

멤버십 동영상의 경우, 인증을 위해 쿠키 파일이 필요합니다.
기본 경로: youtube_video/youtube_cookies.txt
쿠키 파일이 없으면 Enter를 눌러 수동 로그인으로 진행.
쿠키 파일 생성 방법:
Chrome/Firefox에서 EditThisCookie 확장 프로그램 설치.
YouTube에 로그인한 상태에서 쿠키를 Netscape 형식(.txt)으로 내보냄.
파일을 youtube_video/youtube_cookies.txt에 저장.




Selenium 사용 여부:

일반 동영상: Selenium 사용 여부 선택 (y/n).
멤버십 동영상: Selenium이 자동으로 활성화.
브라우저 프로필 경로를 입력하여 저장된 쿠키를 사용할 수 있음 (선택).


동영상 URL 입력:

YouTube 동영상 URL을 입력 (예: https://www.youtube.com/watch?v=VIDEO_ID).


액션 선택:

1: youtube_video 폴더에 동영상 다운로드.
2: VLC 또는 기본 플레이어로 재생.
3: .mp4 URL을 클립보드에 복사.
사용 가능한 포맷(화질, 해상도, FPS)을 선택.


CSV 저장:

동영상 메타데이터를 youtube_video 폴더에 CSV 파일로 저장할지 선택 (y/n).



출력

다운로드된 동영상: youtube_video/*.mp4
메타데이터: youtube_video/youtube_video_info_*.csv
쿠키 파일: youtube_video/youtube_cookies.txt (수동 로그인 후 자동 저장)

멤버십 동영상 다운로드

로그인 필수: YouTube의 보안 정책상, 멤버십 동영상은 로그인(인증) 없이는 다운로드 또는 시청이 불가능합니다.
쿠키 파일 사용:
한 번 쿠키 파일을 생성하면 반복적인 로그인 불필요.
youtube_video/youtube_cookies.txt에 저장된 쿠키를 자동으로 사용.


수동 로그인:
쿠키 파일이 없으면 Selenium이 브라우저를 열어 수동 로그인을 요청.
로그인 후 쿠키가 youtube_video/youtube_cookies.txt에 저장되어 이후 자동화.


제한사항:
로그인 없이 멤버십 동영상에 접근하려는 시도는 YouTube 서버에 의해 차단됩니다.
정당한 멤버십 구독자 자격으로만 사용하세요.



문제 해결

IndentationError:
코드 들여쓰기가 잘못된 경우 발생. 편집기에서 탭 대신 4칸 공백 사용 확인.
VS Code 설정: Tab Size: 4, Insert Spaces 활성화.


멤버십 동영상 에러:
"Members-only" 오류 발생 시, 유효한 쿠키 파일(youtube_video/youtube_cookies.txt) 제공 또는 수동 로그인.
쿠키 파일이 만료되었으면 새로 내보내기.


Selenium 오류:
Chrome과 ChromeDriver 버전 호환성 확인.
webdriver-manager로 최신 ChromeDriver 설치:pip install webdriver-manager




다운로드 실패:
인터넷 연결 확인.
URL이 올바른지, 멤버십 동영상인지 확인.
쿠키 파일이 유효한지 재확인.
