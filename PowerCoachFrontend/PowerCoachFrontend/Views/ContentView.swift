//
//  ContentView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 1/16/25.
//

import SwiftUI

struct ContentView: View {
    //@State changes the variable within a VIEW
    //The shared WebSocketManager, which is initialized in WebSocketManager, is set to webSocketManager. It is a ViewModel instance.
    
    var body: some View {
        TabView {
            //Home
            Tab("Home", systemImage: "house.fill") {
                HomeView()
            }
            Tab("POWERCOACH", systemImage: "dumbbell.fill") {
                PowerCoachView()
            }
            Tab("Profile", systemImage: "person.crop.circle.fill") {
                ProfileView()
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager.shared)
}
