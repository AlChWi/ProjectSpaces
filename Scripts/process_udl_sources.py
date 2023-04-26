import tomllib
import os.path
import subprocess
import sys
import hashlib

class UDLProcessor:
    uniffi_bin_path: str
    input_file_path: str
    output_dir_path: str
    swift_files_dir_name: str
    c_files_dir_name: str

    def __init__(
        self,
        uniffi_bin_path: str, 
        input_file_path: str,
        output_dir_path: str,
        swift_files_dir_name: str,
        c_files_dir_name: str
    ) -> None:
        self.uniffi_bin_path = uniffi_bin_path
        self.input_file_path = input_file_path
        self.output_dir_path = output_dir_path
        self.swift_files_dir_name = swift_files_dir_name
        self.c_files_dir_name = c_files_dir_name

    def run_bindgen(self) -> None:
        module_name = os.path.basename(self.input_file_path).removesuffix(".udl")
        lock_file_path = os.path.join(self.output_dir_path, f"{module_name}_udl.lock")
        with open(self.input_file_path, 'rb') as udl_file:
            udl_file_contents = udl_file.read()
            new_checksum = hashlib.md5(udl_file_contents).hexdigest()
        if os.path.exists(lock_file_path):
            with open(lock_file_path, 'rb') as lock_file:
                old_checksum = lock_file.read()
            if old_checksum == new_checksum:
                print(f"No changes in {self.input_file_path}. Skipping FFI generation step.")
                return
        else:
            with open(lock_file_path, "w") as lock_file:
                lock_file.write(new_checksum)

        cwd = os.getcwd()
        nwd = os.path.join(cwd, self.uniffi_bin_path)
        print("Processing UDL files with uniffi...")
        sources_dir_path = os.path.join(self.output_dir_path, "Sources")
        args = [   
            "cargo", "run",
            f"--manifest-path={nwd}/Cargo.toml",
            "generate",
            self.input_file_path,
            "--language", "swift",
            "--out-dir",
            sources_dir_path
        ]
        uniffi_process = subprocess.run(args)
        uniffi_process.check_returncode()

        # Move swift wrapper file to "SwiftWrapper" folder
        swift_wrapper_file_name = module_name + ".swift"
        swift_wrapper_location = os.path.join(sources_dir_path, swift_wrapper_file_name)
        new_swift_wrapper_location = os.path.join(sources_dir_path, self.swift_files_dir_name, swift_wrapper_file_name)
        os.replace(swift_wrapper_location, new_swift_wrapper_location)

        # Move header and modulemap files to "{ModuleName}FFI/include" folder
        header_file_name = module_name + "FFI" + ".h"
        header_file_location = os.path.join(sources_dir_path, header_file_name)
        new_header_file_location = os.path.join(sources_dir_path, self.c_files_dir_name, "include", header_file_name)
        os.replace(header_file_location, new_header_file_location)

        modulemap_file_name = module_name + "FFI" + ".modulemap"
        modulemap_file_location = os.path.join(sources_dir_path, modulemap_file_name)
        new_modulemap_file_location = os.path.join(sources_dir_path, self.c_files_dir_name, "include", modulemap_file_name)
        os.replace(modulemap_file_location, new_modulemap_file_location)


def main():
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir,
        "UDLProcessorConfig.toml"
    )

    with open(file_path, 'rb') as f:
        toml = tomllib.load(f)
    uniffi_path = toml["uniffi"]["path"]
    args = sys.argv
    input_file = args[1]
    output_dir = args[2]
    c_files_dir = args[3]
    swift_files_dir = args[4]
    processor = UDLProcessor(
        uniffi_path,
        input_file,
        output_dir,
        swift_files_dir,
        c_files_dir
    )
    processor.run_bindgen()
    sys.exit(0)


if __name__ == "__main__":
    main()

