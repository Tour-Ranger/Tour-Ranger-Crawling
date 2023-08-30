# 다나와 여행 패키지 크롤러

- 해당 프로젝트는 VSCode와 Window OS를 기본 전제로 하여 설명하고 있음.
- Python 프로젝트 이므로 실행을 위해 VSCode의 Python Extension 설치 필수(설치하면 우상단에 Run 버튼이 생긴다!)
- 크롤링에 사용되는 Chromedriver는 본인의 Chrome 버전에 맞는 버전을 crawler.py와 같은 위치에 설치해야 합니다.([참고 링크](https://kminito.tistory.com/78))


## 초기 환경 구축

### 가상 환경 경로 구성
```bash
$ python -m venv .venv
```
### 가상 환경 활성화
```bash
$ source .venv/Scripts/activate
```
### 필요 패키지 설치
```bash
$ pip install -r requirements.txt
```
### (참고) 가상환경 비활성화
```bash
$ deactivate
```

---

## 주요 사양

- Python : 3.11.0
- selenium : 3.141.0
- Chromedriver : 116.0.5845.96 (window 64)
