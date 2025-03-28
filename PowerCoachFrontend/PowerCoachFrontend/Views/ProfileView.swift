//
//  ProfileView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//


import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack {
            Text("\(webSocketManager.userid)")
                .font(.largeTitle)
                .fontWeight(.black)
                .foregroundColor(Color.red)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .foregroundColor(.black)
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(WebSocketManager.shared)
}
