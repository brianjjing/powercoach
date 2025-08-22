//
//  SingleWorkoutView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/10/25.
//

import SwiftUI

struct SingleWorkoutView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) var dismiss
    
    @State private var editMode = EditMode.inactive
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    @State private var showingDeleteConfirmation = false
    
    @State var workout: Workout //The parameter that needs to be passed
    
    var body: some View {
        VStack {
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach($workoutsViewModel.editedWorkout.exercises, id: \.id) { $exercise in
                        if editMode == .inactive {
                            ExerciseDisplayRow(exercise: exercise, editMode: $editMode)
                        }
                        else {
                            VStack {
                                TextField("Workout Name", text: $workoutsViewModel.editedWorkout.name)
                                    .font(.title3)
                                    .padding()
                                    .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
                                    .background(Color(.systemGray6))
                                    .cornerRadius(10)
                                    .disableAutocorrection(true)
                                    .multilineTextAlignment(.center)
                                    //.focused($amountIsFocused)

                                ExerciseCreationRow(
                                    exercise: $exercise,
                                    availableExercises: workoutsViewModel.createdWorkout.availableExercises,
                                    mode: "edit")
                            }
                        }
                    }
                    .onMove(perform: move)
                    
                    if workoutsViewModel.editWorkoutErrorMessage != nil {
                        Text(String(describing: workoutsViewModel.editWorkoutErrorMessage!))
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                    }
                    if editMode == EditMode.active {
                        Button(action: {
                            workoutsViewModel.addExercise(mode: "edit")
                        }) {
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
            }
            // Removed the redundant toolbar modifier from the ScrollView.
            // This was the source of the "ambiguous use" error.
            
            if editMode == EditMode.active {
                Button(action: {
                    showingDeleteConfirmation = true
                }) {
                    Text("Delete Workout")
                        .padding(.vertical, 20)
                        .padding(.horizontal)
                        .frame(maxWidth: .infinity)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                }
            }
        }
        .padding()
        .background(Color(.systemGroupedBackground))
        .scrollIndicators(.visible)
        // Correctly apply the single toolbar to the top-level container (VStack).
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text(workout.name)
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundStyle(.primary)
            }
            ToolbarItem(placement: .topBarTrailing) {
                EditButton()
            }
        }
        .environment(\.editMode, $editMode)
        .onAppear {
            if let workoutId = workout.workoutId {
                workoutsViewModel.editedWorkout.workoutId = workoutId
            }
            workoutsViewModel.editedWorkout.exercises = workout.exercises
            workoutsViewModel.editWorkoutErrorMessage = nil
        }
        .onDisappear {
            workoutsViewModel.resetEdit()
        }
        .onChange(of: editMode) {
            if editMode == .inactive {
                workoutsViewModel.editWorkout()
            }
        }
        .confirmationDialog("Are you sure?", isPresented: $showingDeleteConfirmation, titleVisibility: .visible) {
            // Confirmation button
            Button("Delete Workout", role: .destructive) {
                Task {
                    await workoutsViewModel.deleteWorkout(workoutToDelete: workout)
                    dismiss()
                }
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("This action cannot be undone.")
        }
    }
    
    func move(from source: IndexSet, to destination: Int) {
        workout.exercises.move(fromOffsets: source, toOffset: destination)
    }
}

#Preview {
    let mockWorkout = Workout(
        name: "Mock Workout",
        exercises: [Exercise(id: UUID(), name: "Push-Ups", sets: 3, reps: 10), Exercise(id: UUID(), name: "Squats", sets: 3, reps: 10)],
        completed: [false, false],
        everyBlankDays: 1,
        today: true
    )
    
    return SingleWorkoutView(workout: mockWorkout)
        .environmentObject(WebSocketManager.shared)
        .environmentObject(WorkoutsViewModel())
}
