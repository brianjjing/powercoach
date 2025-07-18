//
//  WorkoutPlanView.swift
//  PowerCoachTestFrontend
//
//  Created by Brian Jing on 7/17/25.
//

import SwiftUI

struct WorkoutPlanView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        CircleCoach()
        .padding()
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("WORKOUT PLAN")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .foregroundColor(.black)
            }
            ToolbarItem(placement: .topBarTrailing) {
                //Make this a button later
                Image(systemName: "plus.app")
                    .font(.system(size: UIScreen.main.bounds.width/20))
                    .foregroundColor(.white)
            }
        }
    }
}

#Preview {
    WorkoutPlanView()
        .environmentObject(WebSocketManager.shared)
}
