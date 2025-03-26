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
    @StateObject private var webSocketManager = WebSocketManager.shared
    
    var body: some View {
        VStack {
            Spacer()
            CircleImage()
            VStack(alignment: .center) {
                Text("POWERCOACH")
                    .font(.largeTitle)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                //.foregroundStyle(.orange)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .foregroundColor(.black)
                
                Text("Message: \(webSocketManager.detectionString)")
            }
            .padding()
            
            Spacer()
            
            //Tabs at the bottom:
            TabView {
                VStack {
                }
                .tabItem {
                    Image(systemName: "map.fill") // Icon for the tab
                    Text("Map") // Title for the tab
                }

                // Second Tab (Home)
                VStack {
                }
                .tabItem {
                    Image(systemName: "house.fill") // Icon for the tab
                    Text("Home") // Title for the tab
                }
                VStack {
                }
                .tabItem {
                    Image(systemName: "person.fill") // Icon for the tab
                    Text("Profile") // Title for the tab
                }
            }
        }
        .onAppear {
            // This will call the connect() method when the view appears
            webSocketManager.connect()
        }
        .onDisappear {
            // Optionally disconnect when the view disappears
            webSocketManager.disconnect()
        }
    }
    
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

enum GHError: Error {
    case invalidURL
    case invalidResponse
    case invalidData
}
