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
            Spacer()
            CircleImage()
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
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(WebSocketManager.shared)
}
