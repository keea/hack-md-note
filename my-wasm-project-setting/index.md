---
title: 나의 WASM 프로젝트 세팅
date: 2023-02-19 10:00:23
categories: 
tags: ["wasm", "emscripten", "c++"]
---

## TL;DR
emscripten은 c++을 이용해서 웹프로그래밍을 할 수 있다는 것이 너무 매력적이다.
회사 업무로적이나 개인적으로나 관심이 많아 이것저것 시도해보고 있다. 내가 사용하는 방법을 정리하고자 한다.

## 기본적인 방법
[emscripten 공식 홈페이지](https://emscripten.org/docs/getting_started/downloads.html)에서 안내하는 방법이다.
``` shell
# Get the emsdk repo
git clone https://github.com/emscripten-core/emsdk.git

# Enter that directory
cd emsdk

# Fetch the latest version of the emsdk (not needed the first time you clone)
git pull

# Download and install the latest SDK tools.
./emsdk install latest

# Make the "latest" SDK "active" for the current user. (writes .emscripten file)
./emsdk activate latest

# Activate PATH and other environment variables in the current terminal
source ./emsdk_env.sh
```
git에서 `sdk`를 설치한 후 원하는 `emscripten` 버전을 설치. 그 다음 활성화 하는 것이다.

그 후 빌드를 하면 된다. `emcc` 명령어에 빌드할 파일을 추가시키면 된다.
``` shell
./emcc test/hello_world.c -o hello.html
```
`html` 파일도 같이 얻고 싶기 위해서 `-o` 명령어를 사용해 `html`을 얻는다.
자세한 내용은 [여기서](https://emscripten.org/docs/getting_started/Tutorial.html) 확인하면 된다.

하지만 파일이 하나라면 이 방법이 편한데 만약 프로젝트가 크다면 불편하다. cmake를 이용해 빌드하는 방법을 주로 사용한다.

## CMake
나의 프로젝트 구성은 다음과 같다.
```
.
|____cpp
| |____CMakeLists.txt
| |____src
| | |____main.cpp
|____web
```
`cpp` 폴더에는 c++ 프로젝트에 대한 것을 다 포함 시킨다.`web` 폴더에는 web에 관한 파일들을 포함 시킬 예정이다.

CMakeFile 내용은 다음과 같다.
``` cmake
cmake_minimum_required(VERSION 3.0.0)
project(EmscriptenProject VERSION 0.1.0)


add_executable(EmscriptenProject src/main.cpp)

if(EMSCRIPTEN)
set(OUTPUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../web/src)
set_target_properties(EmscriptenProject PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR}
    SUFFIX ".html"
    LINK_FLAGS "-s WASM=1"
)

endif()
```
`OUTPUT_DIR`에 export할 `.wasm`, `.js`, `.html` 경로를 설정해준다.
`SUFFIX`으로 `html` 파일이 익스포트할 거라고 알리고 `LINK_FLAGS`에 emscripten 옵션을 추가해주면 된다. [여기서](https://emscripten.org/docs/tools_reference/emcc.html) 확인하고 필요한 옵션을 추가하면 된다.

해당 `main.cpp`는 `hello world`를 출력하는거라서 많은 옵션을 추가하지 않았다.


빌드 명령어는 다음과 같다.
``` shell
cmake -S . -B ./.web-build --toolchain ./emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake
cmake --build ./.web-build --config Release
```
`CMakeLists.txt` 파일이 존재하는 경로에서 실행하면 된다. 여기서 `--toolchain` 다음 부분에 자신의 emsdk 경로를 추가하면 된다.

빌드 후 파일 구조는 다음과 같다(기타 파일들을 가렸다).
```
.
|____web
| |____src
| | |____EmscriptenProject.js
| | |____EmscriptenProject.wasm
| | |____EmscriptenProject.html
|____cpp
| |____CMakeLists.txt
| |____.web-build
| |____src
| | |____main.cpp
```
`web/scr`에 파일이 추가된 것을 확인할 수 있다. html을 바로 클릭하면 실행할 수 없다. XHR 요청을 지원하지 않으면 `.wasm` 파일을 요청할 수 없기 때문이다. 로컬 웹서버를 사용해야한다. 나는 주로 `vscode`의 [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)를 사용한다.

![](https://hackmd.io/_uploads/Bk96NvkRj.png)
html을 실행하면 `hello world!`가 출력되는 것을 확인할 수 있다.

## 쉘 스크립트 작성
명령어를 일일히 입력하기 귀찮기 때문에 쉘 스크립트를 추가한다. 우선 emscripten을 설치하는 스크립트를 작성했다.
``` sh
# install_emsdk.sh

DIRECTORY="$( cd "$( dirname "$0" )" && pwd -P )"

cd ${DIRECTORY}

# Get the emsdk repo
git clone https://github.com/emscripten-core/emsdk.git

# Enter that directory
cd emsdk

# Fetch the latest version of the emsdk (not needed the first time you clone)
git pull

# Download and install the latest SDK tools.
./emsdk install latest

# Make the "latest" SDK "active" for the current user. (writes .emscripten file)
./emsdk activate latest
```
최초 1회만 실행하면 된다. 그러면 `install_emsdk.sh` 가 위치한 곳에 `emsdk`를 다운받고 설치한다.

그 다음 빌드 명령어도 스크립트로 만든다.
``` sh
# build_web.sh
CURRENT_DIRECTORY="$( cd "$( dirname "$0" )" && pwd -P )"
EMSDK=${CURRENT_DIRECTORY}/emsdk

cmake -S ${CURRENT_DIRECTORY} -B ${CURRENT_DIRECTORY}/.web-build --toolchain "${EMSDK}/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake"
cmake --build ${CURRENT_DIRECTORY}/.web-build --config Release
```
쉘 스크립트 실행으로 빌드까지 할 수 있다. 쉘 스크립트 위치는 `cpp` 폴더에 포함 시켰다.

```
.
|____web
| |____src
| | |____EmscriptenProject.js
| | |____EmscriptenProject.wasm
| | |____EmscriptenProject.html
|____cpp
| |____CMakeLists.txt
| |____build_web.sh
| |____install_emsdk.sh
| |____.web-build
| |____src
| | |____main.cpp
```
빌드 까지 완료한 파일 구조이다.

## 샘플 프로젝트
저장소를 만들었으니 여기서 확인하면 된다.
https://github.com/keea/sample-emscripten-project-template

## 여담
우선 간단한 샘플 만드는 것부터 정리했다. 그 외에 다양한 방법을 연구한 것이 있는데 추후에 문서를 작성하고 여기에 추가하도록 하겠다. 예를 들어 js만 뽑아서 번들링 한다던가... 리엑트와 연동시킨다던가 등등!!

그리고 샘플 저장소의 README는 ChatGPT가 적어줬다.