//
//  WorkoutRow.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/13/25.
//

import SwiftUI

struct WorkoutRowView: View {
    var workout: Workout
    @Environment(\.colorScheme) var colorScheme
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        NavigationLink(destination: SingleWorkoutView(workout: workout)) {
            VStack {
                Text(workout.name)
                    .font(.title3)
                    .fontWeight(.black)
                    .foregroundStyle(.primary)
            }
            .padding(.vertical, 20)
            .padding(.horizontal)
            .frame(maxWidth: .infinity)
            .background(rowBackgroundColor)
            .cornerRadius(12)
        }
        // This is a more robust way to handle width constraints
        .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
    }
}
