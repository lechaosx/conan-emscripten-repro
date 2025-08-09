# Conan Emscripten Repro

The purpose of this repository is to demonstrate unintuitive interaction between `conan`, `cmake-conan`, `cmake` and `emscripten`.

## Development Environment

The environment is managed via `nix` package manager. If you have it, just enter it via

```
nix develop
```

Otherwise feel free to peek into [flake.nix](flake.nix) and make sure to have the dependencies available in you current environment via your favourite approach.

## Experiments

This repository consists of two projects, a `dependency` and a `consumer`. The `dependency` is a dependency of the `consumer`.

The `dependency` consists of trivial `CMakeLists.txt` file that depends on `CMAKE_SIZEOF_VOID_P` variable being defined when `cmake` is configured, and fails to configure when it's not. In real life, this is the case for [godot-cpp](https://github.com/godotengine/godot-cpp) library.

The most trivial case is the native configuration of the dependecy.

```
cmake -DCMAKE_BUILD_TYPE=Release -B dependency/build-native dependency
```

This should always pass as the `CMAKE_SIZEOF_VOID_P` is detected by default by CMake.

The `dependecy` also contains trivial `conanfile.py` recipe. You can export it via

```
conan export dependency
```

or you can even build the package via

```
conan create dependency
```

Given sane default `conan` profile, the build should pass without problem.

The consumer consists of trivial `CMakeLists.txt` that does nothing but finding the `dependecy` package. It also contains `conanfile.txt` that declared dependecy to `dependency`. It demonstrates project that depends on [godot-cpp](https://github.com/godotengine/godot-cpp) library. The intention is to resolve dependency via `conan` package manager.

The most trivial way to satisfy the dependencies via `conan install` explicitly with the `default` profile

```
conan install --output-folder consumer/build-conan-install --build missing consumer
cmake --preset conan-release consumer
```

Given sane default profile, this should pass.

For simplicity of usage, `cmake-conan` can be used to automatically satisfy dependencies via `conan` without explicit `conan install` calls.

```
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=conan_provider.cmake -B consumer/build-cmake-conan consumer
```

This call detects the profile from the current `cmake` environment and uses it to build the dependencies.

Now let's say I want to build the consumer project with `emcscripten`. The package for `emscripten` contains `emcmake` utility that, when prepended before `cmake` call, should pass proper toolchain into `cmake` configure step

```
emcmake cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=conan_provider.cmake -B consumer/build-cmake-conan-emcmake consumer
```

In this case `cmake-conan` scans the environemnt, detects `emscripten`, creates `conan` profile for it and uses the profile for building the dependencies. The build of `dependecy` fails because `CMAKE_SIZEOF_VOID_P` is not defined.

In non-cross-compiling scenarios, CMake build system will automatically fill the `CMAKE_SIZEOF_VOID_P` variable during the first `project()` call. In cross-compiling scenario with no emulator provided, the variable will stay undefined as the build system has no way to extract this value from the `try_compile` artifacts.

One thing you can do is to save the profile. On my machine, the profile detected by `cmake-conan` was

```
[settings]
arch=wasm
os=Emscripten
compiler=clang
compiler.version=20
compiler.libcxx=libc++
build_type=Release
[conf]
tools.cmake.cmaketoolchain:generator=Unix Makefiles
tools.build:compiler_executables={"c":"/nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/emcc","cpp":"/nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/em++"}
```

I will save this profile as `emscripten`. Now it can be used explicitly by `cmake-conan`

```
emcmake cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=conan_provider.cmake -DCONAN_HOST_PROFILE=emscripten -B consumer/build-cmake-conan-emscripten-profile consumer
```

This behaves the same as if the profile is detected and indeed fails again due to `CMAKE_SIZEOF_VOID_P` not beind defined.

One thing that can be done is to explicitly reference the `emscripten` toolchain in the profile via `tools.cmake.cmaketoolchain:user_toolchain` config. On my machine, the toolchain is located at `/nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/cmake/Modules/Platform/Emscripten.cmake`

```
[settings]
arch=wasm
build_type=Release
compiler=clang
compiler.libcxx=libc++
compiler.version=20
os=Emscripten
[conf]
tools.build:compiler_executables={'c': '/nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/emcc', 'cpp': '/nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/em++'}
tools.cmake.cmaketoolchain:user_toolchain=["/nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/cmake/Modules/Platform/Emscripten.cmake"]
```

Let's save this profile as `emscripten-toolchain` and configure the `consumer` with it

```
emcmake cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=conan_provider.cmake -DCONAN_HOST_PROFILE=emscripten-toolchain -B consumer/build-cmake-conan-emscripten-profile-toolchain consumer
```

This indeed configures the `consumer` and properly builds the `dependency` dependency. The `CMAKE_SIZEOF_VOID_P` variable is filled in from the referenced `emscripten` toolchain.



Now let's use the explicit profiles to backtrack.

```
conan install --output-folder consumer/build-conan-install-emscripten-profile-toolchain --profile emscripten-toolchain --build missing consumer
emcmake cmake --preset conan-release consumer
```

As expected, this builds the dependencies and configures the project without an issue, same as `cmake-conan` with the profile explicitly specified via `CONAN_HOST_PROFILE`.

It can also be tried with the `emscripten` profile without the toolchain.

```
conan install --output-folder consumer/build-conan-install-emscripten-profile --profile emscripten --build missing consumer
cmake --preset conan-release consumer
```

Weirdly, this does not behave the same as `cmake-conan` with no profile or the `emscripten` profile specified. At least on my machine, probably due to `nix`, the configuration of the `dependency` fails with following message

```
System is unknown to cmake, create:
Platform/Emscripten to use this system, please post your config file on discourse.cmake.org so it can be added to cmake
-- Detecting C compiler ABI info
System is unknown to cmake, create:
Platform/Emscripten to use this system, please post your config file on discourse.cmake.org so it can be added to cmake
-- Detecting C compiler ABI info - failed
-- Check for working C compiler: /nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/emcc
System is unknown to cmake, create:
Platform/Emscripten to use this system, please post your config file on discourse.cmake.org so it can be added to cmake
-- Check for working C compiler: /nix/store/ld69r25m2x3pn34kapycvwv53v929ggs-emscripten-4.0.11/share/emscripten/emcc - broken
```

The same error is given when building the `dependency` package directly via

```
conan create dependency --profile emscripten
```

When the `emscripten-toolchain` profile is passed, it indeed builds fine

```
conan create dependency --profile emscripten-toolchain
```

As a final sanity check, the `emcmake` can be used to configure the `dependency` directly

```
emcmake cmake -DCMAKE_BUILD_TYPE=Release -B dependency/build-emcmake dependency
```

## Resolution

This works at cost of flexibility and developer experience:
- `emcmake` utility can't be utilized to pass the toolchain. Localtion of the toolchain needs to be known and hardcoded into the profile.
- `cmake-conan` can't be utilized to detect the build environment and automatically pass it to the dependencies.