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


## 겪었던 문제 해결

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
