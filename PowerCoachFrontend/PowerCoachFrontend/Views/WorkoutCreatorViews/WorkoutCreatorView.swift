//
//  WorkoutCreatorView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import SwiftUI

struct WorkoutCreatorView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    var body: some View {
        VStack {
            List {
                
            }
            .listStyle(.plain) // Use .plain to remove the default list dividers and style
            
            Button("Create workout") {
                //Make the action viewModel.createWorkout()
                //Should point to the create_workout url from the viewmodel.
            }
        }
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("WORKOUT CREATOR")
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
    WorkoutCreatorView()
        .environmentObject(WebSocketManager.shared)
}
