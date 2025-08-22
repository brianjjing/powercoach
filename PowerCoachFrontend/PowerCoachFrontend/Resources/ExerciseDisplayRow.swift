//
//  ExerciseDisplayRow.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/13/25.
//

import SwiftUI

struct ExerciseDisplayRow: View {
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    
    var exercise: Exercise
    @Binding var editMode: EditMode
    
    @Environment(\.colorScheme) var colorScheme
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        HStack {
            Text("\(exercise.sets)x\(exercise.reps) \(exercise.name)")
                .font(.title3)
                .fontWeight(.black)
                .foregroundStyle(.primary)
                .multilineTextAlignment(.leading)
                .padding(.vertical, 20)
                .padding(.horizontal)
                .frame(maxWidth: .infinity)
                .background(rowBackgroundColor)
                .cornerRadius(12)
            
            if editMode == EditMode.active {
                Button(action: {
                    DispatchQueue.main.async {
                        workoutsViewModel.deleteExercise(mode: "edit", exercise: exercise)
                    }
                }) {
                    Image(systemName: "trash")
                        .font(.title2)
                        .foregroundStyle(.primary)
                        .foregroundColor(.red)
                }
            }
            
        }
    }
}
