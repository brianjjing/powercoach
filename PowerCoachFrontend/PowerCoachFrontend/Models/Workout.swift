//
//  Workout.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import Foundation

struct CreatedWorkout: Codable {
    var name: String
    var exercises: [Exercise] = [Exercise()]
    var everyBlankDays: Int
    let availableExercises = ["Conventional Deadlifts", "RDLs", "Deep Squats", "Quarter Squats", "Barbell Overhead Presses", "Barbell Bicep Curls", "Barbell Rows"]
}

struct Exercise: Identifiable, Codable {
    var id = UUID()
    var name: String = "Select exercise"
    var sets: Int = 0
    var reps: Int = 0
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
