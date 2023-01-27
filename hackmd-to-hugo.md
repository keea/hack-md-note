---
title: HackMD 글을 Hugo 형태로 변경
date: 2023-01-27 10:46:23
categories: blog
tags: ["blog"]
---

## TL;DR
HackMD라는 마크다운 에디터를 찾았다. 에디터도 마음에 들지만 깃허브로 푸시하여 문서들을 관리할 수 있다. 그렇다면 해당 문서들을 정적 블로그의 포스트로 사용하는 것이 좋다고 생각했고 이 부분을 자동화하고자 했다.

그래서 현재 HackMD에서 작성한 문서를 레파지토리에 푸시하면 hugo 포스트 형식으로 변환하여 hugo 홈페이지에 적용했다.

## date 추가하기
최초 레파지토리에 푸시할 때 자동적으로 `date`를 추가했다. 이것은 아래와 같이 진행했다.

이 부분은 https://fatihkalifa.com/twitter-github-actions 해당 글을 참고하여 작업했다.

``` shell
git diff --name-status HEAD~1 | grep ".md$" | grep "^A" | cut -c 3-
```
`git diff` 명령어를 사용하면 파일의 어떤 내용이 변경되는지 알 수 있다. `HEAD~1`로 가장 최신의 변경 사항을 가져온다. 
- `git diff --name-status HEAD~1` 다음과 같은 결과를 얻을 수 있다.
    
    ```
    M       test34567.md
    A       test555.md
    ```

여기서 원하는 것은 새로 추가된 `test555.md`이다. 그래서 `grep`과 `cut` 명령어를 통해 원하는 것을 파싱을 했다.
- `grep ".md$"` : md 파일 찾는다.
- `grep "^A"` : A로 시작한 것을 찾는다. git diff로 확인하면 맨 처음에 A(Add), M(Modify) 등으로 표시한다.
- `cut -c 3-` : 불필요한 명령어들을 삭제해버린다.

위의 명령어를 실행 시 다음과 같은 결과를 얻었다.
```
test555.md
```
새로 추가된 마크다운 문서의 파일명을 구했으니 `date`를 추가하면 된다.
```
sed -i "/^date:/s/.*/date: `date "+%Y-%m-%d %H:%M:%S"`/g" test555.md
```
`sed` 명령어를 통해 파일의 내용을 변경하도록 했다. `date:` 라는 부분을 찾아 `date: {현재날짜}`로 변경한다. 이걸 하기 위해서는 해당 문서 안에 `date:` 부분이 있어야한다. 

뭐 이 정도는 HackMD의 템플릿 기능을 사용해 자동으로 추가했다.

현재 날짜는 `date`명령어를 통해 구했다. `date "+%Y-%m-%d %H:%M:%S"` 를 사용하여 hugo 형식인 "년-월-일 시간" 포맷을 취할 수 있다.

그 후 변경된 내용을 커밋하면 되는 것이다!!

## hugo 형태의 파일 트리 만들기
이제 날짜를 추가했으니 hugo 홈페이지에 보일 수 있게 파일 구조도 신경써야한다.
```
./content
|____posts
| |____start
| | |____feature.jpg
| | |____index.md
```
내가 사용하는 템플릿 콘텐츠 파일 구조에는 블로그 포스트들을 저장하는 `posts`라는 폴더가 있으며 각 포스트별로 제목(ex:`start`) 폴더 안에 실제 포스트인 `index.md`와 썸네일인 `feature.jpg`로 구성되어 있다.


마크다운 파일 이름을 구해 폴더를 만들고 해당 마크다운의 이름을 index.md로 만들면 된다고 생각했다.
파일명은 위에서 같이 구하면 되고 이름은 `basename` 이라는 명령어를 사용하면 구할 수가 있다고 해서 바로 시작했다.

``` shell
title=$(basename ${{ steps.push-file.outputs.file }} .md)
```
`basename`으로 파일명을 구하고 `.md`명령어로 확장자를 제거해버렸다. 어차피 위에서 md파일만 구하기 때문에 상관 없었다.

이름 변경하는 것이나 파일 위치 변경하는 것은 `mv` 명령어를 사용하면 된다.

이후 나는 `hugo`라는 브런치를 만들어서 따로 관리하고 싶었다. `hugo` 같은 경우도 빌드한 후 빌드의 산출물을 다른 브런치에다가 다 저장하는 것이다. 나도 이걸 하고 싶었다!!

대충 생각한 플로우는 다음과 같다.

0. hugo 사이트에서 `content/post`에 hackmd 저장소를 서브모듈로 등록.
1. hackmd에서 문서 작성 후 푸시.
2. hackmd 저장한 레파지토리에서 hugo 형식에 맞게 변경.
3. 변경 후 hugo 레파지토리도 같이 업데이트.

### 브런치 작업
우선 빈 브런치부터 만들었다. 이런 것을 고아브런치라고 하는 것을 알았다. https://blog.naver.com/writer0713/221611414098 글을 참고해서 `hugo-content` 고아 브런치를 만들었다.

``` shell
git checkout --orphan hugo-content
git rm -rf .
git commit --allow-empty -m "init hugo content"
git push origin hugo-content
```

그 후 위에 작업한 것을 커밋을 하기 위해 새로운 폴더를 만들고 github action 안에서 커밋을 했지만 맘에 들지 않았다. `content/post/start` 로 되어있는 것보다 `post` 폴더 안에 있는 내용물만 푸시하고 싶기 때문이다. 그래서 `peaceiris/actions-gh-pages@v3` 소스코드를 까봤다.

여기서 해결하는 방법은 푸시하고 싶은 내용물이 든 폴더에 `.git` 폴더를 복사해 넣고 커밋한 후 푸시하는 것이다!! 나는 해당 폴더에 `git init`로 초기화 해 다시 다 설정해야하나 생각했는데 `.git`폴더를 복사하면 설정을 다시 안해도 되기 때문에 좋다!!

```
mkdir -p ${dir}/${content}/${title}
cp -r ${dir}/.git ${dir}/${content}
cd ${dir}/${content}
git fetch origin
git checkout hugo-content
mv ${{ steps.push-file.outputs.file }} ${dir}/${content}/${title}/${filename}
git add --all
git config --global user.email ${{ secrets.EMAIL }}
git config --global user.name ${{ secrets.USER_NAME }}
git commit -am "[POST] Add Hugo Post"
git push origin hugo-content
```
폴더 만들고 `.git`파일 복사하고 커밋할 파일 옮기고 커밋하고 푸시하는 것까지 완료했다. 이제 `hugo-content` 브런치에는 hugo 형태의 포스터 파일만 남아있게 되었다!!

## 썸네일 추가하기
간지나게 썸네일도 추가하고 싶었다. 썸네일이 없으니 심심해서 추가하고 싶었다. 근데 썸네일을 찾아서 추가하고 싶지는 않았다. 자동으로 그리는 프로그램을 만들어야 하나??? 아니면 좀 더 빠르게 할 수 있는 방법이 있지 않나 생각보다가 NASA에서 매일마다 우주 사진을 업로드를 해준다는 것이 생각났다.

Astronomy Picture of the Day(https://apod.nasa.gov/apod/astropix.html) 일명 APOD로 우주 사진과 우주에 대한 설명을 해준다. 썸네일로도 괜찮은 것 같고 블로그 스킨에도 잘 어울렸다.

'아 이걸 사용하면 되겠다' 생각하며 좀 더 API(https://api.nasa.gov/)도 제공해준다는 것이다. 이런 것은 빠르게 작성할 수 있는 Python을 이용해서 만들어보았다.

``` python
def fetch_apod(date):
    apod_url = "https://api.nasa.gov/planetary/apod"
    params = {
        'api_key':os.environ.get('APOD_API_KEY'),
        'date':date,
        'hd':'True'
    }
    response = requests.get(apod_url, params=params, timeout=5).json()
    return response["hdurl"]
```

api를 요청하여 이미지 주소를 가져온다. git action 환경변수로 api키를 등록하기 때문에 `os.environ.get('APOD_API_KEY')`를 사용했다.

``` python
def random_date():
    start_date = datetime.today().replace(day=1, month=1, year=2015).toordinal()
    end_date = datetime.today().toordinal()
    return datetime.fromordinal(random.randint(start_date, end_date)).strftime("%Y-%m-%d")

def download_image(url, file_path):
    os.system("curl " + url + " > " + file_path)
```

날짜는 2015년 1월 1일 부터 현재까지의 날짜를 받기로 했다. 같은 날 같은 썸네일은 좀 그래서 랜덤으로 했다. 이미지 다운로드는 그냥 `curl`명령어를 호출 하는 형태로 했다.

git action에서는 다음과 같이 호출하면 된다.
``` shell
python3 ../apod/apod.py ${dir}/${content}/${title}/feature.jpg
```
`apod.py`로 실행하고 인자값은 저장할 파일 경로로 했다. 당연히 인자 값을 넣기 때문에 python에서 해당 부분을 처리를 해주도록 했다.

```
file_path = " ".join(sys.argv[1:len(sys.argv)])
```
풀 소스코드는 다음과 같다.
{{< gist keea 3cb7cc3d3567b9b2876c7972589ef6a7 >}}

## 서브모듈 업데이트
이제 푸시되면 hugo사이트에서 자동으로 업데이트를 하게하면 글쓰는 것 외에 아무것도 신경 안써도 된다!!

``` yml
  Update:
    needs: hugo-format-setting
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          repository: ${{ github.repository_owner }}/keea.github.io
          token: ${{ secrets.PRIVATE_TOKEN_GITHUB }}
      - name: Pull & update submodules recursively
        run: |
          git submodule update --init --recursive
          git submodule update --recursive --remote
      - name: Commit
        run: |
          git config user.email ${{ secrets.EMAIL }}
          git config user.name ${{ secrets.USER_NAME }}
          git add --all
          git commit -m "📝 Update Post" || echo "No changes to commit"
          git push
```
hugo 포맷 설정하는 것이 끝나면 hugo 사이트의 레파지토리를 체크아웃해서 서브모듈 업데이트하고 푸시하면 된다. 아쉽게도 템플릿도 서브모듈로 등록되었기 때문에 같이 업데이트 해줄 것이다.
`PRIVATE_TOKEN_GITHUB`은 https://github.com/settings/tokens 에서 토큰 만들고 `Repository secrets` 에 등록하면 된다.

## 마지막으로..
이렇게 HackMD에서 작성한 글을 자동으로 hugo 사이트의 포스트로 만들도록 했다. 생각보다 github action 다루는 것이 어려워 엄청 많은 시도를 했다. 물론 테스트 레파지토리에서... 아직 몇 가지 더 많이 남았지만 우선 이 정도로 마무리 짓고 더 업그레이드 할 것이다.

예를 들어 gist 포맷을 자동으로 바꿔준다던가... 등등

사실 글을 쓰고 날짜 맞춰서 추가해주고 폴더도 만들어서 추가해주는 것이 이걸 만드는 것보다 시간 소모가 덜 될 수도 있다고 생각이 들기는 하지만 이런 것도 신경써야하기 때문에 그냥 자동화 해버렸다.

이제 글 쓰는 것에 집중해야겠다!!!