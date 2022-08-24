## 클래스, DB 구조도


## git commit 메시지 규약

* 구현 타입
* 추가
* 수정
* Chor
* 리팩토링
* 테스트

git commit 메시지 규약 중요하지만, 경험상 대부분의 커밋 타입은 구현(흔히 말하는 Feat)이었다.  
그렇기에 구현이라는 모호한 말보다는 쉽게 특징을 알아볼 수 있게 바꿔봤다.

`UI`, `Back`, `Deploy` 이 3가지 키워드를 구현 타입으로 활용해볼 예정


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


