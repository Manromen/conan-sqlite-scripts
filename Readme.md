# Conan SQLite

This repository contains the conan receipe that is used to build the SQLite packages at [rgpaul bintray](https://bintray.com/manromen/rgpaul).

For Infos about the SQLite library please visit [sqlite.org](https://sqlite.org/).
The library is in the [Public Domain](https://sqlite.org/copyright.html).
This repository is licensed under the [MIT License](LICENSE).

## macOS

To create a package for macOS you can run the conan command like this:

`conan create . sqlite/3.26.0@rgpaul/stable -s os=Macos -s os.version=10.14 -s arch=x86_64 -s build_type=Release -o shared=False`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* [Xcode](https://developer.apple.com/xcode/)
