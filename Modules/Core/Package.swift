// swift-tools-version: 5.8
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Core",
    platforms: [.iOS("17"), .macOS("14")],
    products: [
        .library(
            name: "Core",
            targets: ["Core"]),
    ],
    dependencies: [
        // local packages
        .package(path: "../RustWrappers/"),
        
        // 3rd party
        .package(url: "https://github.com/pointfreeco/swift-composable-architecture", from: .init(0, 52, 0))
    ],
    targets: [
        .target(
            name: "Core",
            dependencies: [
                // local packages
                .product(name: "RustWrappers", package: "RustWrappers"),
                // 3rd party
                .product(name: "ComposableArchitecture", package: "swift-composable-architecture")
            ]
        ),
        .testTarget(
            name: "CoreTests",
            dependencies: ["Core"]),
    ]
)
