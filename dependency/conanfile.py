import conan

class DependencyPackage(conan.ConanFile):
	name = "dependency"
	version = "0.1"
	settings = "os", "arch", "compiler", "build_type"
	exports_sources = "CMakeLists.txt"
	generators = "CMakeToolchain"

	def build(self):
		cmake = conan.tools.cmake.CMake(self)
		cmake.configure()