//
//  ExerciseDisplayRow.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/13/25.
//

import SwiftUI

struct ExerciseDisplayRow: View {
    var workout: Workout
    var index: Int
    @Environment(\.colorScheme) var colorScheme
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        HStack {
            Text("\(workout.sets[index])x\(workout.reps[index]) \(workout.exercises[index])")
                .font(.title3)
                .fontWeight(.black)
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
