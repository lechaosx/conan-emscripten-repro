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

Slighly more complex case is configuration via `emcmake`, which should automatically pass the `emscripten` toolchain into a `cmake` configuration call.

```
emcmake cmake -DCMAKE_BUILD_TYPE=Release -B dependency/build-emscripten dependency
```

This case should pass as the provided toolchain contains explicit definition of `CMAKE_SIZEOF_VOID_P`. The CMake build system will not automatically fill the variable because it is a cross-compilation scenario with no emulator provided.

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