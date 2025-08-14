//
//  Workout.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import Foundation

struct CreatedWorkout: Codable {
    var name: String
    var numExercises: Int
    var exercises: [String] = ["Select exercise"]
    var sets: [Int]
    var reps: [Int]
    var startDateTime: Date
    var everyBlankDays: Int
    let availableExercises = ["conventional_deadlift", "rdl", "deep_squat", "quarter_squat", "standing_overhead_press", "barbell_bicep_curls", "barbell_rows"]
}

struct Workout: Codable {
    let workoutId: Int
    let name: String
    let numExercises: Int
    let exercises: [String]
    let sets: [Int]
    let reps: [Int]
    let completed: [Bool]
    let everyBlankDays: Int
}

struct WorkoutResponse: Codable {
    let homeDisplayMessage: String
    let todaysWorkouts: [Workout]
    let otherWorkouts: [Workout]
}
