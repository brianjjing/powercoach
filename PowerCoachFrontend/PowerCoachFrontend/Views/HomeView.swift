//
//  HomeView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack {
            Text("PWRCCH")
                .font(.largeTitle)
                .fontWeight(.black)
                .foregroundColor(Color.red)
            
            //Add a line or so of space here
            
            //Just make this two buttons:
            HStack {
                Text("My Coach")
                    .font(.headline)
                Text("Workout Tracker")
                    .font(.headline)
                    .fontWeight(.bold)
            }
            
            
            Spacer()
            CircleCoach()
            VStack(alignment: .center) {
                Text("\(webSocketManager.displayString)")
                    .font(.largeTitle)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .foregroundColor(.black)
            }
            .padding()
            
            Spacer()
            Spacer()
            Spacer()
        }
        .onAppear {
            //Start the powercoach stream
            webSocketManager.emit(event: "test_message", with: ["Test homeview"])
            print("Test message sent")
            webSocketManager.emit(event: "handle_powercoach_frame", with: ["sdafjasd;lfkjasd;lkf"])
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(WebSocketManager.shared)
}
