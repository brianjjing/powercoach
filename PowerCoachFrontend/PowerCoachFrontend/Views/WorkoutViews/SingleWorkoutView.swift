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
                //.onMove(perform: move)
                
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
