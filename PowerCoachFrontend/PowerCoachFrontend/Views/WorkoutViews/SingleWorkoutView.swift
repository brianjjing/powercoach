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
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    @State private var showingEditMode = false
    @State private var showingDeleteConfirmation = false
    
    let workout: Workout //The parameter that needs to be passed
    
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(0..<workout.exerciseNames.count, id: \.self) { index in
                    ExerciseDisplayRow(workout: workout, index: index)
                    
//                    Text("\(workout.sets[index])x\(workout.reps[index]) \(workout.exercises[index])")
//                        .font(.title3)
//                        .fontWeight(.bold)
//                        .foregroundStyle(.primary)
//                        .multilineTextAlignment(.leading)
//                        .padding(.vertical, 20)
//                        .padding(.horizontal)
//                        .frame(maxWidth: .infinity)
//                        .background(rowBackgroundColor)
//                        .cornerRadius(12)
                }
                //.onMove(perform: moveExercises)
                
                if showingEditMode { //isPresented only works for other views, not for buttons
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
                Button(action: {
                    // This toggles the state variable to show/hide edit mode
                    showingEditMode.toggle()
                }) {
                    // Changes the icon based on the current edit mode
                    if showingEditMode { //isPresented only works for other views, not for buttons
                        Text("Done")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.blue)
                    } else {
                        Image(systemName: "square.and.pencil")
                            .font(.system(size: UIScreen.main.bounds.width/20))
                            .foregroundColor(.primary)
                    }
                }
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
        .environment(\.editMode, .constant(showingEditMode ? .active : .inactive)) //Sets environment variable for editMode toggled by showingEditMode, which allows for Swift native view editing functionalities.
    }
    
//    private func moveExercises(from source: IndexSet, to destination: Int) {
//        if let currentWorkout = currentWorkout {
//            // Update the local workout state for the UI
//            currentWorkout.exercises.move(fromOffsets: source, toOffset: destination)
//            currentWorkout.sets.move(fromOffsets: source, toOffset: destination)
//            currentWorkout.reps.move(fromOffsets: source, toOffset: destination)
//
//            // Call the view model to handle the data change
//            workoutsViewModel.moveExercises(of: currentWorkout, from: source, to: destination)
//        }
//    }
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
