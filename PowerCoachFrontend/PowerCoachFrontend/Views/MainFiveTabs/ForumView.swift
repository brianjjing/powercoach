//
//  ForumView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 6/23/25.
//

import SwiftUI

struct ForumView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        CircleCoach()
        VStack(alignment: .center) {
            Text("\(webSocketManager.forumDisplay)")
                .font(.title)
                .fontWeight(.black)
                .foregroundColor(Color.red)
                .foregroundStyle(.secondary)
                .foregroundColor(.black)
                .multilineTextAlignment(.center)
        }
        .padding()
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("MY CHATS")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
            }
            ToolbarItem(placement: .topBarTrailing) {
                NavigationLink(destination: InProgressView()) {
                    Image(systemName: "square.and.pencil")
                        .font(.system(size: UIScreen.main.bounds.width/20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
}

#Preview {
    ForumView()
        .environmentObject(WebSocketManager.shared)
}
