//
//  WorkoutCreatorView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import SwiftUI

struct WorkoutCreatorView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    var body: some View {
        VStack {
            TextField("Workout Name", text: $workoutsViewModel.createdWorkout.name)
                .font(.title3)
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(10)
                .disableAutocorrection(true)
                .multilineTextAlignment(.center)
            
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(0..<workoutsViewModel.createdWorkout.numExercises, id: \.self) { index in
                        ExerciseCreationRow(index: index, createdWorkout: $workoutsViewModel.createdWorkout)
                    }
                    
                    if workoutsViewModel.workoutCreatorViewErrorMessage != nil {
                        Text(String(String(describing: workoutsViewModel.workoutCreatorViewErrorMessage)))
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                    }
                    Button(action: workoutsViewModel.addExercise) {
                        Text("Add Exercise")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .padding()
                            .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                }
            }
            .padding()
            .background(Color(.systemGroupedBackground))
            .scrollIndicators(.visible)
            
            if let errorMessage = workoutsViewModel.errorMessage {
                Text(errorMessage)
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundColor(.red)
            }
            
            Button(action: workoutsViewModel.createWorkout) {
                Text("Create Workout")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .padding()
                    .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
                    .background(Color.blue)
                    .cornerRadius(10)

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
