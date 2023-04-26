//
//  ContentView.swift
//  ProjectSpaces
//
//  Created by Oleksii Perov on 4/25/23.
//

import SwiftUI
import Core

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundColor(.accentColor)
            Text(Core().text)
        }
        .padding()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
