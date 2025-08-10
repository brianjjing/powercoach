//
//  InProgressView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/2/25.
//

import SwiftUI

struct InProgressView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        CircleCoach()
        VStack(alignment: .center) {
            Text("This feature is coming in a later update!")
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
                Text("POWERCOACH")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
            }
        }
    }
}

#Preview {
    InProgressView()
        .environmentObject(WebSocketManager.shared)
}
