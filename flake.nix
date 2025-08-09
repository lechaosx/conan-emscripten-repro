{
	inputs = {
		nixpkgs.url = "github:NixOS/nixpkgs";
	};

	outputs = { nixpkgs, ... }:
	let
		pkgs = import nixpkgs { system = "x86_64-linux"; };
	in {
		devShells.x86_64-linux.default = pkgs.mkShell {
			buildInputs = with pkgs; [
				gcc
				cmake
				conan
				emscripten
			];
		};
	};
}
