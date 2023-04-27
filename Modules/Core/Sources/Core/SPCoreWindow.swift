//
//  SPCoreWindow.swift
//  
//
//  Created by Oleksii Perov on 4/27/23.
//

import ComposableArchitecture
import SwiftUI

struct SPCoreWindow: View {
    let store: StoreOf<SPCoreReducer>
    
    var body: some View {
        WithViewStore(store, observe: { $0 }) { store in
            Text(store.text)
        }
    }
}
