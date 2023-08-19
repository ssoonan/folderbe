## folderbe : group your youtube channels by folder

이 프로젝트는 제 **필요**에서 시작 됐습니다.  
전 유튜브를 영어, 일본어, 프로그래밍 등 자기개발 용도로만 활용하고 싶었습니다. 하지만 유튜브는 맞춤 추천 영상으로 절 현혹합니다.  
이에 저는 제가 원하는 채널만 구독하고, 그 채널들의 영상만 보고 싶었습니다.

하지만 구독 채널은 많아지지만 구독 채널들을 모아서 관리하는 기능은 유튜브에 없었습니다.

이에 저는 이 채널들을 **폴더** 형식으로 모으고, 해당 폴더의 영상들만 보는 서비스가 있으면 좋겠다는 생각을 합니다. 그리고 이를 되도록 라이브러리 없이 *밑바닥*부터 직접 개발하며 개발 실력도 익히고자 폴더브 프로젝트를 시작했습니다.


## install

### prerequisite

- docker, docker-compose
- python3
- youtube API 사용을 위한 OAuth 세팅

```bash
# 가상환경 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# local DB 세팅
docker-compose up -d db
flask init-db  # create SQL로 DB 세팅
```

### ENV
```
.env 내
CLIENT_ID
CLIENT_SECRET
FLASK_CONFIG=development
FLASK_DEBUG=1
```

세팅이 다 된 이후
`flask run`로 실행

## 화면 기획

https://chrome.google.com/webstore/detail/pockettube-youtube-subscr/kdmnjgijlmjgmimahnillepgcgeemffb

유사 서비스로 크롬 확장인 pockettube가 있었습니다. 하지만 이 확장은  
1. 쓰기가 불편함
2. 어쨌든 유튜브 사이트를 들어가야함

이런 한계로 pockettube의 화면은 참고하되, 직접 웹 서비스로 만들기로 결정했습니다.

https://ovenapp.io/view/765IxdhUfSIBt9EtNuZGVW6nKaabtbQK/l6Gm4  
카카오 오븐으로 정말 간단하게 기획했다. 기획을 한 차례 하고 친구의 피드백을 받아  
채널 추가, 삭제는 hover시에만 뜨게 변경하였다.

## 클래스, DB 구조도

<img src="diagrams/folderbe%20classdiagram.jpeg" width=500>  
<img src="diagrams/folderbe%20db.jpeg" width=500>  

개발을 시작하기 전, 최소한의 생각으로 설계를 진행

## git commit 메시지 규약

* UI
* Back
* 구현
* Deploy
* Test
* Fix
* Chor
* Refactor

git commit 규약도 중요하지만, 메시지만 보고 직관적으로 알 수 있으면 그만이다.  

UI, Back, 구현, Deploy, Test인 기능 파트  
수정인 Fix, Chor, Refactor  
그 밖인 Ex

이 키워드들로 commit message를 시작, 직관적인 문장으로 commit 할 예정 


## 문제 해결 과정

### session이 유지 되지 않던 문제

`refresh_token`기능을 넣었음에도 session 내의 데이터가 다 사라지는 문제 발생  
조사 결과 flask의 session은 `parmanent` 옵션 기본값이 `False`로 설정이 되어있어 브라우저를 닫으면 세션이 초기화됨  
`session.parmanent = True` 코드를 로그인 시에 설정 함으로써 문제 해결


### flask redirect시 http method가 변경되지 않는 문제

js의 `fetch`로 폴더 생성 및 삭제를 HTTP `POST`, `DELETE` 메서드로 구현  
에러 검사 후 문제가 없으면 flaskredirect로 화면을 재갱신함  
이 때 GET으로 redirect 되지 않고 DELETE 메서드로 요청이 `한 번` 더 가는 문제가 발생

즉, 같은 폴더 삭제를 `2번` 요청함. flask에서 400 error 처리를 해서 큰 문제는 없지만 요청이 2번 가는 문제의 원인을 찾을 수 없었음.  
flask의 redirect를 통한 새로고침이 문제인 건 간접적으로 파악했지만, 이 기능을 직접 바꾸긴 어려웠다.  
대신 js의 `window.location.reload()`로 화면 새로고침을 대신함

역시 문제 해결의 과정은 하나만 있지 않다.

### DB의 id를 프론트에서 볼 수 있음에 따른 보안 문제

폴더 삭제, 폴더에 따른 채널 확인 시 폴더의 id로 해당 폴더를 db에서 찾음
이 때 따로 프론트 프레임워크를 쓰는 게 아닌 vanilla js 코드를 넣다보니 이 id값이 html 상에 그대로 노출이 됨  

url 상에서 id를 숨기는 방식으로 구현할 수도 있지만, 그럼에도 html 상에서 id가 노출이 되기에 이 id 값으로 다른 사용자의 폴더 확인, 삭제가 가능  

그렇기에 매번 폴더에 대한 요청이 올 때마다, user의 id로 검사해 내 폴더가 아닌 다른 폴더를 사용할 시 403 에러를 반환하게 변경


## 리팩토링 과정

### DAO 직접 구현

ORM을 직접 가져다 쓰는 게 아닌 최소한의 wrapper인 pymysql을 활용해 DaO를 직접 구현하였다.  
이 과정에서 mysql connection, cursor를 open 및 close를 해야했다.  

이 부분이 insert, update 등 기능마다 중복이 일어나서 공통부분을 DaO라는 클래스로 만들고  
UserDaO, FolderDao 등이 dao를 싱글턴으로 가져와 활용하게 리팩토링 했다.


## 개선할 점

### 기획 시 최소 기능만 남기기

무턱대고 사이드 프로젝트를 시작했지만, 폴더브의 핵심은 구독한 채널 중에서도 보고 싶은 _일부_ 만을 보는 것이었다. 

그렇다면 제일 처음 버전은 굳이 폴더를 만드는 기능이 없어도 되지 않았을까?  


### test 진행 시의 DB 환경

pytest로 유닛 테스트를 할 때도 같은 DB를 쓰는데, 그러다 보니  
실제 기능을 테스트할 때와 유닛 테스트 할 때 DB가 겹치는 문제가 발생  

초기엔 유닛 테스트 완료 후 DB를 drop 했는데, 그러다보니 기능 테스트를 할 때 매번 회원가입을 해야 하는  
번거로운 문제 발생

비즈니스 로직만 테스트하고 싶은데 플라스크 환경을 만들어야 하고, 그게 귀찮다보니 테스트 작성도 어려워짐

-> 이런 테스트 시 환경을 따로 만드는 mock이라는 게 있었다.  
결국 이 문제는 **의존성**의 문제. 나름 DAO를 만들고 layer 계층을 분리해보려 했다.  
그럼에도 flask, db 등이 탄탄이 묶여 있으니 테스트를 하기가 용이하지 않았다.



### 프론트와 서버 사이드 렌더링의 명확한 분리

프론트와 백을 프레임워크 별로 나눈 게 아니라 하나의 flask app으로 프로젝트를 구성.  
그러다 보니 어떤 역할을 js에서 하고 어떤 역할을 flask에서 할지가 겹칠 때가 있다.

> 예를 들어 각 폴더에 채널을 추가하는 모달에서, 채널들의 목록은 서버 사이드에서 미리 렌더링해서 보내준다.

```html
{% for channel in channels %}
  <label class="modal__channel d-flex align-items-center pt-2 pb-2">
    <input data-folder_ids="{{ channel.folder_ids }}" class="modal__channel--checkbox" type="checkbox" name="{{ channel.channel_id }}" value="true">
    <div class=""><img class="modal__channel--avatar" src="{{ channel.icon_img }}" alt=""></div>
    <span class="modal__channel--name">{{ channel.name }}</span>
  </label>
{% endfor %}
```

이러면 js가 받을 때부터 이미 html 태그로 만들어져서 온다.   
하지만 서버 사이드 렌더링 만으로 원하는 기능을 구현하지 못하면 js를 써야 하는데,  
이 때 이게 기능마다 명확하지 않아서 내가 혼자 개발할 때도 혼란을 야기할 때가 있었음


### Dao parameter, return 값의 통일

언제는 id를 인자로, 언제는 model을 인자로 받음  
언제는 model을 return, 언제는 id를 return함

이게 통일 되어있지 않고 지금처럼 세부사항에 의존하면, 기능이 변경될 때마다 연결된 코드가 매번 바뀌어야함.  


### model의 역할 없음

그동안 했던 ORM 기반 설계에서 계층에 대한 이해를 하고자  
`model`은 추상화된 도메인, `Dao`는 DB와 연결된 영속성, 이렇게 계층을 나눔.

하지만 웬만한 비즈니스 로직은 SQL로 이뤄지기에 Dao에서 대부분의 기능을 구현.  
현재 `model`에 있는 `class`들은 *데이터를 옮기는 인스턴스*에 불과

도메인 주도 설계 & 의존 역전을 적용해 model에 기능을 넣고, 추상화하여 변화에 둔감하게 만들면 좋으리라 생각


## TODO

- [x] 로그인 개선 - refresh token 기능 붙여서
  - + JWT 고려하기
- [x] JS 채널 목록 검색 기능
- [x] 무한 스크롤로 과거 영상 로딩 기능
- [x] 랜딩 페이지, 로그인 화면
- [ ] 개발 or 배포 환경 config 분리
  - [ ] config 따라 달라지는 로직
  - [ ] 의존 주입으로
- [ ] 프러덕션 환경에서의 DB 마이그레이션 고려, 현재는 DB 변경 시 직접 SQL문을 쏴야함


이후
- [x] OAuth 동의 consent 화면 계속 띄우기
- [ ] 앱 심사 받고 공개, 이후 SEO, GA 붙이기
- [ ] 폴더 내 영상 검색 기능
- [ ] 모바일 반응형, or APP 개발 시 API로 전환 고려