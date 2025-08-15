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
    @Environment(\.colorScheme) var colorScheme
    
    @FocusState private var amountIsFocused: Bool
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
                .focused($amountIsFocused)
            
            ScrollView {
                LazyVStack(spacing: 12) {
                    // FIX: Iterate directly over the array of `Exercise` objects
                    // using `id: \.id`. This gives each view a stable, unique
                    // identifier that is independent of its position in the array.
                    ForEach($workoutsViewModel.createdWorkout.exercises) { $exercise in
                        ExerciseCreationRow(
                            exercise: $exercise,
                            availableExercises: workoutsViewModel.createdWorkout.availableExercises
                        )
                    }
                    
                    if workoutsViewModel.workoutCreatorViewErrorMessage != nil {
                        Text(String(describing: workoutsViewModel.workoutCreatorViewErrorMessage!))
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
            if amountIsFocused {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") {
                        amountIsFocused = false
                    }
                }
            }
        }
    }
}


#Preview {
    WorkoutCreatorView()
        .environmentObject(WebSocketManager.shared)
}
