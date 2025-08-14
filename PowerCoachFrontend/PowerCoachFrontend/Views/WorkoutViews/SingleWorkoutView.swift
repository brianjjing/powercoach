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
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    let workout: Workout //The parameter that needs to be passed
    
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(0..<workout.numExercises, id: \.self) { index in
                    HStack {
                        Text("\(workout.sets[index])x\(workout.reps[index]) \(workout.exercises[index])")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundStyle(.primary)
                            .multilineTextAlignment(.leading)
                    }
                    .padding(.vertical, 20)
                    .padding(.horizontal)
                    .frame(maxWidth: .infinity)
                    .background(rowBackgroundColor)
                    .cornerRadius(12)
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
                Button(action: editWorkout) {
                    Image(systemName: "square.and.pencil") //Be able to add and delete exercises, rename workout + exercises, and delete the workout.
                        .font(.system(size: UIScreen.main.bounds.width/20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
    
    private func editWorkout() {
        // This is where you would put the logic for editing the workout.
        // For example, you could show an edit sheet or navigate to a new view.
        print("Edit workout button tapped for \(workout.name)")
        
        // This function has access to the workout parameter and your EnvironmentObjects
        // webSocketManager.emit(...)
        // workoutsViewModel.someFunction(...)
    }
}

#Preview {
    let mockWorkout = Workout(
        workoutId: 1,
        name: "Mock Workout",
        numExercises: 2,
        exercises: ["Pushups", "Squats"],
        sets: [3, 3],
        reps: [10, 10],
        completed: [false, false],
        everyBlankDays: 1
    )

    
    SingleWorkoutView(workout: mockWorkout)
        .environmentObject(WebSocketManager.shared)
        .environmentObject(WorkoutsViewModel())
}
