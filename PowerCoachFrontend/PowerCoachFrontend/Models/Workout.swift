//
//  Workout.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

struct Workout: Codable {
    let name: String
    let num_exercises: Int
    let exercises: [String]
    let sets: [Int]
    let reps: [Int]
    let weights: [Int]
}

struct WorkoutResponse: Codable {
    let home_display_message: String
    let workouts: [Workout]
}
