---
title: 나의 WASM 프로젝트 세팅 - embind
date: 2023-03-25 21:11:30
categories: 
tags: ["wasm", "emscripten", "c++"]
---

## TL;DR
이전글([나의 WASM 프로젝트 세팅]([/Ah1TusfNSIqb77QU-eoVjw](https://keea.github.io/posts/my-wasm-project-setting/))) 에서 c++ 코드를 웹에서 실행할 수 있게 되었다. 하지만 이전에는 main함수의 내용을 바로 실행했다면 이번에는 c++ 함수나 클래스를 자바스크립트에서 호출하고자 한다!!

## embind
embind는 c++ 함수나 클래스를 자바스크립트에 바인딩 하는 기술이다. 위에서 말했듯이 c++ 함수나 클래스를 자바스크립트에서 호출 하거나, c++ 객체를 생성할 수 있다.

## embind 사용 방법
`EMSCRIPTEN_BINDINGS` 매크로를 사용하여 C++ 코드에서 바인딩 할 클래스 및 함수를 정의하면 된다.

``` c++
#include <emscripten/bind.h>

int Add(int a, int b) {
  return a + b;
}

EMSCRIPTEN_BINDINGS(add_binding) {
  emscripten::function("Add", &Add);
}
```

`int Add(int, int)` 함수를 자바스크립트에서 노출할 수 있도록 했다.

해당 코드를 `lembind` 옵션을 사용하여 컴파일 하면 된다.

``` shell
emcc -lembind -o add.js add.cpp
```

웹에서는 다음과 같이 사용하면 된다.

``` html
<!doctype html>
<html>
  <script>
    var Module = {
      onRuntimeInitialized: function() {
        console.log('lerp result: ' + Module.add(1, 2));
      }
    };
  </script>
  <script src="add.js"></script>
</html>

```
`onRuntimeInitialized`를 사용하여 런타임이 준비되었을 때 코드를 실행한다.

## 번들링
물론 c++로 뽑아낸 자바스크립트만 사용하는 경우도 있지만 다른 자바스크립트들과 사용할 경우 묶어서 사용하는 번들링 기술을 사용하는 것도 좋다고 생각해서 번들링을 설정했다.

### Rollup
여러가지 번들링 도구 중 Rollup을 사용한 큰 이유는 없다. 그냥 내가 보기에 간단해 보이고 성공했기 때문이다. 

## Install
필요한 플러그인을 다운받았다.

``` shell
npm install -D rollup @rollup/plugin-commonjs @rollup/plugin-node-resolve rollup-plugin-polyfill-node
```
- @rollup/plugin-commonjs : CommonJS 모듈 형식으로 작성된 코드를 ES 모듈 형식으로 변환한다.
- @rollup/plugin-node-resolve : 외부 모듈(node_modules) 사용 시 사용한다.
- rollup-plugin-polyfill-node : Node.js 환경에서 사용 가능한 전역 객체나 함수를 브라우저에서 사용할 수 있도록 polyfill을 제공한다.

이러한 용도로 해당 플러그인을 설정했다.

## Setting
``` .js
import commonjs from '@rollup/plugin-commonjs';
import {nodeResolve} from '@rollup/plugin-node-resolve';
import nodePolyfills from 'rollup-plugin-polyfill-node';

export default {
  input: 'index.js',
  output: {
    file: './dist/index.js',
    format: 'umd',
    name: 'Wasm',
  },
  plugins: [nodeResolve(), commonjs(), nodePolyfills()]
};
```

index.js를 진입점으로 설정하고 output 설정을 해주었다. format은 umd를 사용하여 모듈 방식을 커버할 수 있도록 했다.

이제 wasm 글루코드를 번들링해보도록 한다.

```
-s WASM=1 -lembind -s MODULARIZE=1 -s 'EXPORT_NAME=\"wasm\"'
```
옵션은 다음과 같이 지정했다.

`MODULARIZE`을 추가한 이유는 익스포트한 자바스크립트가 모듈 형태로 되는 것도 있고, 이 모듈이 factory 함수 형태 반환하는데 factory 함수를 호출하면, 생성된 모듈이 다운로드되고 인스턴스화되는 과정이 진행되며 factory 함수가 반환하는 Promise가 resolved가 된다고 한다.

로딩이 완료되는 시점에 c++로 바인딩한 함수를 사용할 수 있게 된다. 로드가 안된 상태에서 불러오는 불상사를 막을 수 있다.

https://emscripten.org/docs/getting_started/FAQ.html#how-can-i-tell-when-the-page-is-fully-loaded-and-it-is-safe-to-call-compiled-functions 해당 링크를 확인하면 된다.


``` js
import wasm from './src/EmscriptenProject.js';

async function Init() {
    let wasmModule;
    await wasm().then(function(Module) { wasmModule = Module });
    return wasmModule;
}

export {Init};
```
롤업의 input인 `index.js`이다. 간단하게 모듈을 로드를 하고 완료되면 모듈을 반환하도록 만들었다.

```
rollup -c
```
해당 명령어를 통해 번들링을 진행하면 `dist`폴더에 번들링된 `index.js` 파일이 생긴다. 여기서 주의할 점은 `dist`폴더 안에 `.wasm`파일도 있어야한다. 이 경로로 `.wasm` 파일을 옮겨주면 된다.

`html` 스크립트를 로드하고 사용하면 된다.
``` html
<!doctype html>
<html>
  <script src="index.js"></script>
  <script type="Module">
    var wasmModule = await Wasm.Init();
    console.log(wasmModule.Add(1,1));
  </script>
</html>
```

html의 로그를 확인해보면 c++로 바인딩한 Add함수가 실행되는 것을 알 수 있다.

## 스크립트 작업
현재는 c++ 빌드 -> 번들링하는 작업 이렇게 2가지 작업이 진행된다. 이걸 자동화를 해보자.

[이전글](https://keea.github.io/posts/my-wasm-project-setting/) 빌드 명령어 스크립트를 실행하면 번들링까지 되도록 하면 된다.

`CMakeLists.txt`에 다음의 코드를 추가하면 된다.
```
set(ROLLUP_OPTS ${CMAKE_CURRENT_SOURCE_DIR}/../web/rollup.config.mjs)
ADD_CUSTOM_COMMAND(TARGET EmscriptenProject 
    COMMAND cd ${CMAKE_CURRENT_SOURCE_DIR}/../web && npx rollup -c ${ROLLUP_OPTS}
    COMMAND ${CMAKE_COMMAND} -E copy ${OUTPUT_DIR}/EmscriptenProject.wasm ${CMAKE_CURRENT_SOURCE_DIR}/../web/dist
    )
```
소스 코드가 빌드 될 때 실행되는 커스텀 명령어를 정의했다. 웹 관련 코드가 저장되어 있는 디렉토리로 작업 디렉토리를 변경하고, 롤업의 설정파일을 실행했다. 그러면 롤업 설정에 따라 dist 디렉토리에 번들링한 index.js가 생성되었을 것이다.
그 다음 코드는 `wasm` 파일을 dist 파일로 복사한다.

이러면 c++ 빌드할 때 자동으로 번들링까지 진행된다!!!

이제 취향껏 package.json의 scripts에 작성을 추가하면 된다.

## 여담
자바스크립트나 웹 환경을 잘 모르는 초보 개발자가 해냈습니다. 추후에 라이브러리나 SDK로 배포를 하게 된다면 최종적으로 사용자가 쓰는 부분은 깔끔하게 간단하게 쓰이는 것이 좋다고 생각해서 이것저것 조사해보고 시행착오 끝냈다.

나름 검색해도 정보가 사혼의 조각처럼 흩어졌기 때문에 정리했다!! 이제는 좀 더 작게작게 emscripten의 팁을 올려야겠다.