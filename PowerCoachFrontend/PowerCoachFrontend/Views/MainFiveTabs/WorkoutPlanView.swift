//
//  WorkoutTrackerView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 6/20/25.
//

import SwiftUI

struct WorkoutPlanView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
        VStack(alignment: .center) {
            CircleCoach()
            
            VStack(alignment: .center) {
                Text("\(webSocketManager.workoutPlanDisplay)")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .foregroundStyle(.secondary)
                    .foregroundColor(.black)
                    .multilineTextAlignment(.center)
            }
            
        }
        .padding()
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("WORKOUT PLAN")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
            }
            ToolbarItem(placement: .topBarTrailing) {
                NavigationLink(destination: InProgressView()) {
                    Image(systemName: "plus.app")
                        .font(.system(size: UIScreen.main.bounds.width/20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
}

#Preview {
    WorkoutPlanView()
        .environmentObject(WebSocketManager.shared)
}
