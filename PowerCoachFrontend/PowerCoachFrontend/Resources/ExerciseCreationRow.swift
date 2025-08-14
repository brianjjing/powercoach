//
//  ExerciseCreationRow.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/12/25.
//

import SwiftUI

struct ExerciseCreationRow: View {
    var index: Int
    @Binding var createdWorkout: CreatedWorkout
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        HStack {
            VStack {
                HStack(spacing: 2) {
                    Text("Sets:")
                        .font(.body)
                    
                    Picker("Sets", selection: $createdWorkout.sets[index]) {
                        ForEach(0...12, id: \.self) { number in
                            Text ("\(number)")
                        }
                    }
                    .background(Color(.systemGray6))
                }
                
                HStack(spacing: 2) {
                    Text("Reps:")
                        .font(.body)
                    
                    Picker("Reps", selection: $createdWorkout.reps[index]) {
                        ForEach(0...12, id: \.self) { number in
                            Text ("\(number)")
                        }
                    }
                    .background(Color(.systemGray6))
                }
            }
            
                
            ExerciseMenu(
                selectedExercise: $createdWorkout.exercises[index],
                availableExercises: createdWorkout.availableExercises
            )
            
            Spacer()
            
            Button(action: workoutsViewModel.addExercise) {
                Image(systemName: "trash")
                    .font(.system(size: UIScreen.main.bounds.width/20))
                    .foregroundStyle(.primary)
                    .foregroundColor(.red)
            }
        }
        .padding(.vertical, 20)
        .padding(.horizontal)
        .frame(maxWidth: .infinity)
        .background(rowBackgroundColor)
        .cornerRadius(12)
    }
}

struct ExerciseMenu: View {
    // The binding connects directly to the exercise string in the parent view's array.
    @Binding var selectedExercise: String
    let availableExercises: [String]
    
    var body: some View {
        Menu(selectedExercise) {
            ForEach(availableExercises, id: \.self) { exercise in
                Button(action: {
                    selectedExercise = exercise
                }) {
                    Text(exercise)
                }
            }
        }
        .font(.body)
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}
