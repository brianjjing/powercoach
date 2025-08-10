//
//  Workout.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

struct Workout: Codable {
    let workout_id: Int
    let name: String
    let num_exercises: Int
    let exercises: [String]
    let sets: [Int]
    let reps: [Int]
    let weights: [Int]
    let completed: [Bool]
    let every_blank_days: Int
}

struct WorkoutResponse: Codable {
    let home_display_message: String
    let todays_workouts: [Workout]
    let other_workouts: [Workout]
}
