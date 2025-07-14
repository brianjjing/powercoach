//
//  ContentView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 7/12/25.
//

import SwiftUI

struct ContentView: View {
    
    var body: some View {
        NavigationStack {
            VStack() {
                
                Spacer()
                
                NavigationLink {
                    PowerCoachView(webSocketManager: WebSocketManager.shared)
                } label: {
                    VStack {
                        PowerCoachTabIcon()
                    }
                }
        
                
            }
        }
        
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager.shared)
}
