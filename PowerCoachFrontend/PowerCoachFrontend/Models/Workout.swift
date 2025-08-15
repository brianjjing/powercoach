//
//  Workout.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import Foundation

struct CreatedWorkout: Codable {
    var name: String
    var exercises: [String]
    var sets: [Int]
    var reps: [Int]
    var everyBlankDays: Int
    let availableExercises = ["Conventional Deadlifts", "RDLs", "Deep Squats", "Quarter Squats", "Barbell Overhead Presses", "Barbell Bicep Curls", "Barbell Rows"]
}

struct Workout: Codable {
    let workoutId: Int
    let name: String
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
