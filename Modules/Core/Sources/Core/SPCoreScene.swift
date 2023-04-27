//
//  SPCoreScene.swift
//
//
//  Created by Oleksii Perov on 4/27/23.
//

import ComposableArchitecture
import SwiftyRustWrapper
import SwiftUI

public struct SPCoreScene: Scene {
    typealias Reducer = SPCoreReducer
    private let store = StoreOf<Reducer>(initialState: Reducer.State(), reducer: Reducer())
    
    public var body: some Scene {
        WindowGroup {
            SPCoreWindow(store: store)
        }
        #if os(macOS)
        MenuBarExtra("TODO", systemImage: "globe") {
            SPMenuBarView(store: store)
        }
        #endif
    }
    
    public init() {}
}

struct SPCoreReducer: ReducerProtocol {
    struct State: Equatable {
        var text = helloFromRust().text
    }
    enum Action: Equatable {
        case buttonTapped
    }
    
    func reduce(into state: inout State, action: Action) -> EffectTask<Action> {
        return .none
    }
}
