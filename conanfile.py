from conans import ConanFile, CMake, tools
import os

class SQLiteConan(ConanFile):
    name = "sqlite"
    version = "3.26.0"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "android_ndk": "ANY", "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine."
    url = "https://github.com/Manromen/conan-sqlite-scripts"
    license = "Public Domain"
    exports_sources = "cmake-modules/*", "CMakeLists.txt"

    def alternateVersion(self):
        splitVersion = self.version.split(".")

        major = splitVersion[0]
        minor = splitVersion[1]
        patch = splitVersion[2]

        if len(minor) == 1:
            minor = '0' + minor

        if len(patch) == 1:
            patch = '0' + patch

        return (major + minor + patch + "00")

    # download sources
    def source(self):
        url = "https://www.sqlite.org/2018/sqlite-amalgamation-%s.zip" % self.alternateVersion()
        tools.get(url)

    # compile using cmake
    def build(self):

        cmake = CMake(self)
        cmake.verbose = True

        cmake.definitions["SQLITE3_VERSION"] = self.alternateVersion()

        if self.settings.os == "Android":
            self.applyCmakeSettingsForAndroid(cmake)

        if self.settings.os == "iOS":
            self.applyCmakeSettingsForiOS(cmake)

        if self.settings.os == "Macos":
            self.applyCmakeSettingsFormacOS(cmake)

        cmake.configure()
        cmake.build()
        cmake.install()

    def applyCmakeSettingsForAndroid(self, cmake):
        android_toolchain = os.environ["ANDROID_NDK_PATH"] + "/build/cmake/android.toolchain.cmake"
        cmake.definitions["CMAKE_SYSTEM_NAME"] = "Android"
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = android_toolchain
        cmake.definitions["ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
        cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(self.settings.arch)
        cmake.definitions["ANDROID_STL"] = self.options.android_stl_type
        cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
        cmake.definitions["ANDROID_TOOLCHAIN"] = "clang"

    def applyCmakeSettingsForiOS(self, cmake):
        ios_toolchain = "cmake-modules/Toolchains/ios.toolchain.cmake"
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = ios_toolchain
        cmake.definitions["DEPLOYMENT_TARGET"] = "10.0"
        variants = []

        if self.settings.arch == "x86":
            cmake.definitions["IOS_PLATFORM"] = "SIMULATOR"
        elif self.settings.arch == "x86_64":
            cmake.definitions["IOS_PLATFORM"] = "SIMULATOR64"
        else:
            cmake.definitions["IOS_PLATFORM"] = "OS"

        # define all architectures for ios fat library
        if "arm" in self.settings.arch:
            variants = ["armv7", "armv7s", "armv8", "armv8.3"]

        # apply build config for all defined architectures
        if len(variants) > 0:
            archs = ""
            for i in range(0, len(variants)):
                if i == 0:
                    archs = tools.to_apple_arch(variants[i])
                else:
                    archs += ";" + tools.to_apple_arch(variants[i])
            cmake.definitions["ARCHS"] = archs
        else:
            cmake.definitions["ARCHS"] = tools.to_apple_arch(self.settings.arch)

    def applyCmakeSettingsFormacOS(self, cmake):
        cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

    def package(self):
        self.copy("*", dst="include", src='include')
        self.copy("*.lib", dst="lib", src='lib', keep_path=False)
        self.copy("*.dll", dst="bin", src='bin', keep_path=False)
        self.copy("*.so", dst="lib", src='lib', keep_path=False)
        self.copy("*.dylib", dst="lib", src='lib', keep_path=False)
        self.copy("*.a", dst="lib", src='lib', keep_path=False)
        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include']

    def package_id(self):
        if "arm" in self.settings.arch and self.settings.os == "iOS":
            self.info.settings.arch = "AnyARM"

    def config_options(self):
        # remove android specific option for all other platforms
        if self.settings.os != "Android":
            del self.options.android_ndk
            del self.options.android_stl_type
