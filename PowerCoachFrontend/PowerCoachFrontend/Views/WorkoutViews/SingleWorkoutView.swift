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
    
    @State var newWorkout = Workout?
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
                    ForEach(workout.exerciseNames, id: \.self) { name in
                        ExerciseDisplayRow(workout: workout, exerciseName: name)
                    }
                    .onMove(perform: move)
                    
                    if workoutsViewModel.addExerciseErrorMessage != nil {
                        Text(String(describing: workoutsViewModel.addExerciseErrorMessage!))
                            .font(.headline)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                    }
                    if editMode == EditMode.active { //isPresented only works for other views, not for buttons
                        Button(action: {
                            workoutsViewModel.addExerciseToExisting(existingWorkout: workout)
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
            
            if editMode == EditMode.active { //isPresented only works for other views, not for buttons
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
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text(workout.name)
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
            }
            ToolbarItem(placement: .topBarTrailing) {
                EditButton()
            }
        }
        .environment(\.editMode, $editMode)
        .onAppear {
            workoutsViewModel.addExerciseErrorMessage = nil
            workoutsViewModel.deleteWorkoutErrorMessage = nil
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
        workout.exercises?.move(fromOffsets: source, toOffset: destination)
    }
}

#Preview {
    let mockWorkout = Workout(
        name: "Mock Workout",
        exerciseNames: ["Pushups", "Squats"],
        sets: [3, 3],
        reps: [10, 10],
        completed: [false, false],
        everyBlankDays: 1,
        today: true
    )

    
    SingleWorkoutView(workout: mockWorkout)
        .environmentObject(WebSocketManager.shared)
        .environmentObject(WorkoutsViewModel())
}
