//
//  ExerciseCreationRow.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/12/25.
//

import SwiftUI

struct ExerciseCreationRow: View {
    @Binding var exercise: Exercise
    let availableExercises: [String]
    
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    @Environment(\.colorScheme) var colorScheme
    
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        HStack {
            VStack {
                HStack(spacing: 2) {
                    Text("Sets:")
                        .font(.body)
                    
                    Picker("Sets", selection: $exercise.sets) {
                        ForEach(0...12, id: \.self) { number in
                            Text ("\(number)")
                        }
                    }
                    .background(Color(.systemGray6))
                }
                
                HStack(spacing: 2) {
                    Text("Reps:")
                        .font(.body)
                    
                    Picker("Reps", selection: $exercise.reps) {
                        ForEach(0...12, id: \.self) { number in
                            Text ("\(number)")
                        }
                    }
                    .background(Color(.systemGray6))
                }
            }
            
            ExerciseMenu(
                selectedExercise: $exercise.name,
                availableExercises: availableExercises
            )
            
            Spacer()
            
            // FIX: Pass the item itself to be deleted, not its index.
            // This is safer because the ID is stable. The ViewModel can find the index to delete.
            Button(action: { workoutsViewModel.deleteExercise(exercise: exercise) }) {
                Image(systemName: "trash")
                    .font(.title2)
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
