from conans import tools, ConanFile, CMake

import os


class FirebaseCppSDK(ConanFile):
    name = 'firebase-cpp-sdk'
    version = '6.16.1'
    description = 'The Firebase C++ SDK provides a C++ interface on top of Firebase for iOS and Android.'
    homepage = 'https://firebase.google.com/docs/cpp/setup'
    license = 'Apache-2.0 License'
    url = 'https://github.com/conan-burrito/firebase-cpp-sdk'

    generators = 'cmake', 'cmake_find_package_multi'

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'with_admob': [True, False],
        'with_analytics': [True, False],
        'with_authentication': [True, False],
        'with_cloud_functions': [True, False],
        'with_cloud_messaging': [True, False],
        'with_cloud_storage': [True, False],
        'with_dynamic_links': [True, False],
        'with_realtime_database': [True, False],
        'with_remote_config': [True, False],
    }
    default_options = {
        'with_admob': True,
        'with_analytics': True,
        'with_authentication': True,
        'with_cloud_functions': True,
        'with_cloud_messaging': True,
        'with_cloud_storage': True,
        'with_dynamic_links': True,
        'with_realtime_database': True,
        'with_remote_config': True,
    }

    no_copy_source = True
    build_policy = 'missing'

    def configure(self):
        if self.settings.os == 'Android' and int(str(self.settings.os.api_level)) < 16:
            raise Exception('Minimal API level is 16')

        if self.options.with_admob and not self.options.with_analytics:
            raise Exception('AdMob requires analytics')

    @property
    def source_subfolder(self):
        return 'src'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('firebase_cpp_sdk', self.source_subfolder)

    def collect_library_names(self):
        names = ['app']
        if self.options.with_admob:
            names.append('admob')

        if self.options.with_analytics:
            names.append('analytics')

        if self.options.with_authentication:
            names.append('auth')

        if self.options.with_cloud_functions:
            names.append('functions')

        if self.options.with_cloud_messaging:
            names.append('messaging')

        if self.options.with_cloud_storage:
            names.append('storage')

        if self.options.with_dynamic_links:
            names.append('dynamic_links')

        if self.options.with_realtime_database:
            names.append('database')

        if self.options.with_remote_config:
            names.append('remote_config')

        return ['firebase_{}'.format(x) for x in names]

    def copy_windows_libs(self):
        runtime = str(self.settings.compiler.runtime)
        if runtime.endswith('d'):
            build_type = 'Debug'
        else:
            build_type = 'Release'

        if runtime.startswith('MT'):
            runtime = 'MT'
        else:
            runtime = 'MD'

        arch = str(self.settings.arch)
        if arch not in ['x86', 'x86_64']:
            raise Exception('Unsupported arch value: %s', arch)

        arch = {'x86_64': 'x64'}.get(arch, arch)

        names = self.collect_library_names()
        for name in names:
            src_dir = os.path.join(self.source_subfolder, 'libs', 'windows', 'VS2015', runtime, arch, build_type)
            self.copy('{}.lib'.format(name), dst='lib', src=src_dir, keep_path=False)

    def copy_linux_libs(self):
        arch = str(self.settings.arch)
        if arch not in ['x86', 'x86_64']:
            raise Exception('Unsupported arch value: %s', arch)

        # Convert conan arch to firebase arch
        arch = {'x86': 'i386'}.get(arch, arch)

        names = self.collect_library_names()
        for name in names:
            src_dir = os.path.join(self.source_subfolder, 'libs', 'linux', arch)
            self.copy('lib{}.a'.format(name), dst='lib', src=src_dir, keep_path=False)

    def copy_android_libs(self):
        libcpp = str(self.settings.compiler.libcxx)
        if libcpp not in ['c++_static']:
            raise Exception('Unsupported libc++ value: %s', libcpp )

        arch = str(self.settings.arch)
        if arch not in ['armv7', 'armv7hf', 'armv8', 'mips', 'mips64', 'x86', 'x86_64']:
            raise Exception('Unsupported arch value: %s', arch)

        # Convert conan arch to firebase arch
        arch = {
            'armv7': 'armeabi-v7a',
            'armv7hf': 'armeabi-v7a-hard',
            'armv8': 'arm64-v8a',
            'x86': 'i386'
        }.get(arch, arch)

        # Convert conan libcpp to firebase libcpp
        libcpp = {
            'c++_static': 'c++'
        }.get(libcpp, libcpp)

        android_root = os.path.join(self.source_subfolder, 'libs', 'android')
        names = self.collect_library_names()
        for name in names:
            src_dir = os.path.join(android_root, arch, libcpp)
            self.copy('lib{}.a'.format(name), dst='lib', src=src_dir, keep_path=False)

        self.copy('*.pro', dst=os.path.join('share', 'proguard'), src=android_root, keep_path=False)
        self.copy('*.gradle', dst=os.path.join('share', 'gradle'), src=self.source_subfolder, keep_path=False)

    def copy_macos_libs(self):
        arch = str(self.settings.arch)
        if arch not in ['universal', 'x86_64']:
            raise Exception('Unsupported arch value: %s', arch)

        names = self.collect_library_names()
        for name in names:
            src_dir = os.path.join(self.source_subfolder, 'libs', 'darwin', arch)
            self.copy('lib{}.a'.format(name), dst='lib', src=src_dir, keep_path=False)

    def copy_ios_libs(self):
        arch = str(self.settings.arch)
        if arch not in ['universal', 'armv8', 'armv7', 'x86', 'x86_64']:
            raise Exception('Unsupported arch value: %s', arch)

        # Convert conan arch to firebase arch
        arch = {'armv8': 'arm64', 'x86': 'i386'}.get(arch, arch)

        names = self.collect_library_names()
        for name in names:
            src_dir = os.path.join(self.source_subfolder, 'libs', 'ios', arch)
            self.copy('lib{}.a'.format(name), dst='lib', src=src_dir, keep_path=False)

    def package(self):
        self.copy('*.py', dst='bin', src=self.source_subfolder, keep_path=False)

        self.copy('*.h', dst='include', src=os.path.join(self.source_subfolder, 'include'), keep_path=True)
        os_name = str(self.settings.os)
        if os_name == 'Windows':
            return self.copy_windows_libs()
        elif os_name == 'Linux':
            return self.copy_linux_libs()
        elif os_name == 'Macos':
            return self.copy_macos_libs()
        elif os_name == 'Android':
            return self.copy_android_libs()
        elif os_name == 'iOS':
            return self.copy_ios_libs()
        else:
            raise Exception('Unsupported OS: %s' % os_name)

    def package_info(self):
        self.cpp_info.libs = self.collect_library_names()

        if self.settings.os == 'Macos':
            self.cpp_info.exelinkflags = ['-framework CoreFoundation', '-framework Security']
        if self.settings.os == 'Android':
            self.cpp_info.libs.append('log')
