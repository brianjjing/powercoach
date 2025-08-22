//
//  WorkoutCreatorView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import SwiftUI

struct WorkoutCreatorView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    @Environment(\.colorScheme) var colorScheme
    
    @State private var editMode = EditMode.active
    @FocusState private var amountIsFocused: Bool
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    // State to control the confirmation dialog
    @State private var showingCancelAlert = false
    
    var body: some View {
        VStack {
            TextField("Workout Name", text: $workoutsViewModel.createdWorkout.name)
                .font(.title3)
                .padding()
                .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
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
                            availableExercises: workoutsViewModel.createdWorkout.availableExercises,
                            mode: "create"
                        )
                    }
                    .onMove(perform: move)
                    
                    if workoutsViewModel.addExerciseErrorMessage != nil {
                        Text(String(describing: workoutsViewModel.addExerciseErrorMessage!))
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                    }
                    
                    Button(action: {workoutsViewModel.addExercise(mode: "create")} ) { //Closure is a runnable block of code and allows a function to represent the functionality and not the returned result
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
            
            if let errorMessage = workoutsViewModel.createWorkoutErrorMessage {
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
        .environment(\.editMode, $editMode)
        .onAppear {
            workoutsViewModel.addExerciseErrorMessage = nil
            workoutsViewModel.createWorkoutErrorMessage = nil
        }
    }
    
    func move(from source: IndexSet, to destination: Int) {
        workoutsViewModel.createdWorkout.exercises.move(fromOffsets: source, toOffset: destination)
    }
}


#Preview {
    WorkoutCreatorView()
        .environmentObject(WebSocketManager.shared)
}
