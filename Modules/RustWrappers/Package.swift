// swift-tools-version: 5.8
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "RustWrappers",
    products: [
        // Products define the executables and libraries a package produces, making them visible to other packages.
        .library(
            name: "RustWrappers",
            targets: ["SwiftyRustWrapper"]),
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .target(
            name: "SwiftyRustWrapper",
            dependencies: [.target(name: "SpacesFFI"), .target(name: "spaces_lib")]
        ),
        .binaryTarget(
            name: "spaces_lib",
            path: "../../../spaces_lib/target/universal/libspaces_lib.xcframework"
        ),
        .target(
            name: "SpacesFFI",
            dependencies: [.target(name: "spaces_lib")]
        ),
        .testTarget(
            name: "RustWrappersTests",
            dependencies: ["SwiftyRustWrapper", "SpacesFFI", "spaces_lib"]),
    ]
)
