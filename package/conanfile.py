import conan
import os

class ReproPackage(conan.ConanFile):
	name = "repro_sizeof_void_p"
	version = "0.1"
	settings = "os", "arch", "compiler", "build_type"
	exports_sources = "dummy.cpp", "CMakeLists.txt"
	generators = "CMakeToolchain", "CMakeDeps"

	def layout(self):
		conan.tools.cmake.cmake_layout(self)

	def build(self):
		cmake = conan.tools.cmake.CMake(self)
		cmake.configure()
		cmake.build()

	def package(self):
		conan.tools.files.copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
		conan.tools.files.copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)

	def package_info(self):
		self.cpp_info.libs = conan.tools.files.collect_libs(self)