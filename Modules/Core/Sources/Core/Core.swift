import SwiftyRustWrapper

public struct Core {
    public private(set) var text = helloFromRust().text
    
    public init() {}
}
