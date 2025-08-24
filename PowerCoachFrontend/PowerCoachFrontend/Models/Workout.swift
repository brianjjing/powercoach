//
//  Workout.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/4/25.
//

import Foundation

let availableExercises = ["Conventional Deadlifts", "RDLs", "Deep Squats", "Quarter Squats", "Barbell Overhead Presses", "Barbell Bicep Curls", "Barbell Rows"]

struct CreatedWorkout: Codable {
    var name: String
    var exercises: [Exercise]
    var everyBlankDays: Int
    let availableExercises = ["Conventional Deadlifts", "RDLs", "Deep Squats", "Quarter Squats", "Barbell Overhead Presses", "Barbell Bicep Curls", "Barbell Rows"]
}

struct EditedWorkout: Codable {
    var workoutId: Int?
    var name: String
    var exercises: [Exercise]
    var everyBlankDays: Int
    let availableExercises = ["Conventional Deadlifts", "RDLs", "Deep Squats", "Quarter Squats", "Barbell Overhead Presses", "Barbell Bicep Curls", "Barbell Rows"]
}

//This is for working with ...
struct Exercise: Identifiable, Codable, Hashable {
    var id: UUID
    var name: String = "Select exercise"
    var sets: Int = 0
    var reps: Int = 0
}

struct Workout: Codable {
    // This property holds the optional ID from the backend.
    // It is optional because a newly created workout won't have an ID yet.
    var workoutId: Int? //Will be None in createWorkout, since SQL deals with the creation.
    var name: String
    var exercises: [Exercise]
    var completed: [Bool]
    var everyBlankDays: Int
    var today: Bool
}

struct WorkoutResponse: Codable {
    let homeDisplayMessage: String
    let workouts: [Workout]
}
