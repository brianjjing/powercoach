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
    
    let workout: Workout //The parameter that needs to be passed
    
    var body: some View {
        List {
            ForEach(0..<workout.num_exercises, id: \.self) {index in
                Text("\(workout.sets[index])x\(workout.reps[index]) \(workout.exercises[index])")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundStyle(.primary)
            }
            .padding()
        }
        .padding()
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
        workout_id: 1,
        name: "Mock Workout",
        num_exercises: 2,
        exercises: ["Pushups", "Squats"],
        sets: [3, 3],
        reps: [10, 10],
        weights: [0, 0],
        completed: [false, false],
        every_blank_days: 1
    )

    
    SingleWorkoutView(workout: mockWorkout)
        .environmentObject(WebSocketManager.shared)
        .environmentObject(WorkoutsViewModel())
}
