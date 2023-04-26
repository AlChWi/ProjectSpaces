import sys
import os.path
import subprocess
import shutil
import typing

class BuildConfiguration:
    architecture: str
    platform: str

    def __init__(self, architecture, platform) -> None:
        self.architecture = architecture
        self.platform = platform

def error_help(error_description: str) -> None:
    error_msg = "It looks like something went wrong building the rust Universal Binary"
    print(f"error: {error_msg}. {error_description}.")

def flatten(list):
    return [item for sublist in list for item in sublist]

def main():
    print("main")
    if len(sys.argv) != 5:
        error_help(
            "Incorrect arguments count. Expected usage: " +
            "path/to/build-scripts/xc-universal-binary.sh" +
            "<STATIC_LIB_NAME> <FFI_TARGET> <SRC_ROOT_PATH> <buildvariant>, " +
            f"recieved: {sys.argv}"
        )
        sys.exit(1)

    # check arguments passed from xcode
    static_lib_name = sys.argv[1]
    ffi_target = sys.argv[2]
    src_root = sys.argv[3]
    build_variant = sys.argv[4].lower()
    print(f"warning: {build_variant}")

    build_flag = "--release" if build_variant == "release" else None
    build_dir = "release" if build_variant == "release" else "debug" 
    target_dir = os.path.join(src_root, "target")

    x86_ios_sim_config = BuildConfiguration("x86_64", "x86_64-apple-ios")
    arm64_ios_config = BuildConfiguration("arm64", "aarch64-apple-ios")
    arm64_ios_sim_config = BuildConfiguration("arm64", "aarch64-apple-ios-sim")
    arm64_macos_config = BuildConfiguration("arm64", "aarch64-apple-darwin")

    configurations = [
        x86_ios_sim_config,
        arm64_ios_config,
        arm64_ios_sim_config,
        arm64_macos_config
    ]
    for config in configurations:
        args = [   
            "cargo", "build",
            f"--manifest-path={src_root}/Cargo.toml",
            "--locked",
            "-p",
            ffi_target,
            "--lib",
            build_flag,
            "--target", config.platform
        ]
        args = filter(None, args)
        process = subprocess.run(args)
        process.check_returncode()

    universal_binary_dir = os.path.join(
        target_dir,
        "universal"
    )
    universal_binary = os.path.join(
        universal_binary_dir,
        static_lib_name.replace(".a", ".xcframework")
    )

    # if the universal binary doesnt exist, or if it's older than the static libs,
    # we need to run `lipo` again.
    lib_dirs = [
        os.path.join(target_dir, platform, build_dir, static_lib_name)
            for platform in map(lambda x: x.platform, configurations)
    ]
    check_if_framework_is_outdated = lambda x: os.path.getctime(x) > os.path.getctime(universal_binary)
    if (
        not os.path.exists(universal_binary) 
        or any(map(
                check_if_framework_is_outdated, list(lib_dirs)
            ))
    ):
        print("Rebuilding Rust library...")

        if not os.path.exists(universal_binary_dir):
            os.makedirs(universal_binary_dir)
        # combine different archs for same platform (i.e. x86/arm64 sim) with lipo
        lipo_output = os.path.join(universal_binary_dir, "sim_lib.a")
        lipo_args = [
            "lipo", 
            "-create",
            "-output",
            lipo_output,
            os.path.join(target_dir, x86_ios_sim_config.platform, build_dir, static_lib_name),
            os.path.join(target_dir, arm64_ios_sim_config.platform, build_dir, static_lib_name)
        ]
        lipo_process = subprocess.run(lipo_args)
        lipo_process.check_returncode()
        # combine different platforms (i.e. sim/phone) into an xcframework
        if os.path.exists(universal_binary):
            shutil.rmtree(universal_binary)
        xcbuild_lib_args = [
            "-library", f"{target_dir}/{arm64_ios_config.platform}/{build_dir}/{static_lib_name}",
            "-library", lipo_output,
            "-library", f"{target_dir}/{arm64_macos_config.platform}/{build_dir}/{static_lib_name}"
        ]
        xcodebuild_args = [
            "xcodebuild",
            "-create-xcframework",
            *[arg for arg in xcbuild_lib_args],
            "-output",
            universal_binary
        ]
        print(xcodebuild_args)
        xcodebuild_process = subprocess.run(xcodebuild_args)
        xcodebuild_process.check_returncode()
        
    sys.exit(0)

if __name__ == "__main__":
    main()