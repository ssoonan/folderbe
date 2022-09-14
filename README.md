## 클래스, DB 구조도


## git commit 메시지 규약

* UI
* Back
* Deploy
* Test
* Fix
* Chor
* Refactor
* Ex

git commit 규약도 중요하지만, 메시지만 보고 직관적으로 알 수 있으면 그만이다.  

UI, Back, Deploy, Test인 기능 파트  
수정인 Fix, Chor, Refactor  
그 밖인 Ex

이 키워드들로 commit message를 시작, 직관적인 문장으로 commit 할 예정



## 리팩토링 과정

### DAO 직접 구현

ORM을 직접 가져다 쓰는 게 아닌 최소한의 wrapper인 pymysql을 활용해 DaO를 직접 구현하였다.  
이 과정에서 mysql connection, cursor를 open 및 close를 해야했다.  

이 부분이 insert, update 등 기능마다 중복이 일어나서 공통부분을 DaO라는 클래스로 만들고  
UserDaO, FolderDao 등이 dao를 싱글턴으로 가져와 활용하게 리팩토링 했다. 


## 문제 해결 과정

### session이 유지 되지 않던 문제

`refresh_token`기능을 넣었음에도 session 내의 데이터가 다 사라지는 문제 발생  
조사 결과 flask의 session은 `parmanent` 옵션 기본값이 `False`로 설정이 되어있어 브라우저를 닫으면 세션이 초기화됨  
`session.parmanent = True` 코드를 로그인 시에 설정 함으로써 문제 해결


### flask redirect시 http method가 변경되지 않는 문제

js의 `fetch`로 폴더 생성 및 삭제를 HTTP `POST`, `DELETE` 메서드로 구현  
에러 검사 후 문제가 없으면 redirect로 화면을 재갱신함  
이 때 GET으로 redirect 되지 않고 DELETE 메서드로 요청이 한 번 더 가는 문제가 발생

즉, 같은 폴더 삭제를 2번 요청함. flask에서 400 error 처리를 해서 큰 문제는 없지만 요청이 2번 가는 문제의 원인을 찾을 수 없었음.  
flask의 redirect가 문제인 건 파악했지만, 이 기능을 직접 바꾸긴 어려워서  
js의 `window.location.reload()`로 화면 새로고침을 대신함

역시 문제 해결의 과정은 하나만 있지 않다.



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

예를 들어 각 폴더에 채널을 추가하는 모달에서, 채널들의 목록은 서버 사이드에서 미리 렌더링해서 보내준다.

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
이 때 이게 기능마다 명확하지 않아서 내가 혼자 개발할 때도 혼란을 야기할 때가 있다.


### Dao parameter, return 값의 통일

언제는 id를 인자로, 언제는 model을 인자로 받음  
언제는 model을 return, 언제는 id를 return함

이걸 하나로 통일할 필요가 있지 않을까? 지금은 너무 세부사항에 의존하는 경향이 있다.  

## TODO

- [ ] 전체 채널 동기화 기능을 효율적으로 할 방법. 현재는 token이 refresh 될 때마다인 1시간 간격으로 됨
- [ ] 개발, 프러덕션, 테스트에 따라 config 값을 주입 받을 수 있게 의존 주입 기능