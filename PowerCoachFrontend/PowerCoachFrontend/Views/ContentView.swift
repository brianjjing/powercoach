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
    @State var currentTab: Int = 1
    
    var body: some View {
        NavigationStack {
            Group {
                switch currentTab {
                case 1:
                    HomeView()
                case 3:
                    ProfileView()
                default:
                    HomeView()
                }
            }
            
            HStack {
                
                Spacer()
                
                Button {
                    DispatchQueue.main.async {
                        currentTab = 1
                    }
                } label: {
                    VStack (alignment: .center, spacing: 4) {
                        Image(systemName: "house.fill")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 24, height: 24)
                        Text("Home")
                            .font(.subheadline)
                    }
                }
                
                Spacer()
                
                NavigationLink {
                    PowerCoachView(webSocketManager: WebSocketManager.shared)
                } label: {
                    VStack {
                        Spacer()
                        Spacer()
                        PowerCoachTabIcon() //Make this shit smaller
                        Spacer()
                        Spacer()
                        Spacer()
                    }
                }
                
                Spacer()
                
                Button {
                    DispatchQueue.main.async {
                        currentTab = 3
                    }
                } label: {
                    VStack (alignment: .center, spacing: 4) {
                        Image(systemName: "person.crop.circle.fill")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 30, height: 30)
                        Text("Profile")
                            .font(.subheadline)
                    }
                }
                
                Spacer()
                
            }
        }
        
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager.shared)
}
