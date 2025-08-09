import conan

class ReproPackage(conan.ConanFile):
	name = "repro_sizeof_void_p"
	version = "0.1"
	settings = "os", "arch", "compiler", "build_type"
	exports_sources = "CMakeLists.txt"
	generators = "CMakeToolchain", "CMakeDeps"

	def layout(self):
		conan.tools.cmake.cmake_layout(self)

	def build(self):
		cmake = conan.tools.cmake.CMake(self)
		cmake.configure()
		cmake.build()