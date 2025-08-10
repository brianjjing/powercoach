//
//  WorkoutTrackerView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 6/20/25.
//

import SwiftUI

struct WorkoutPlanView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel //Env object is found by TYPE, not name, so it can have a diff name here.
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        VStack(alignment: .center) {
            if (workoutsViewModel.todaysWorkouts.isEmpty) && (workoutsViewModel.otherWorkouts.isEmpty) {
                
                Spacer().frame(height: UIScreen.main.bounds.height/5)
                
                Text("You haven't created any workouts. Create one using the plus button on the top right!")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundStyle(.primary)
                    .foregroundColor(buttonTextColor)
                    .multilineTextAlignment(.center)
            }
            else {
                Text("Select a workout below or create one with the plus button on the top right!")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(buttonTextColor)
                    .foregroundStyle(.primary)
                    .multilineTextAlignment(.center)
                
                ScrollView {
                    LazyVStack(spacing: 12) {
                        // Workout_id is the unique identifier
                        ForEach(workoutsViewModel.todaysWorkouts, id: \.workout_id) {workout in
                            NavigationLink(destination: SingleWorkoutView(workout: workout)) {
                                VStack {
                                    Text(workout.name)
                                        .font(.title)
                                        .fontWeight(.black)
                                        .foregroundStyle(.primary)
                                        .foregroundColor(.black)
                                        .multilineTextAlignment(.center)
                                }
                                .padding(.vertical, 20)
                                .padding(.horizontal)
                                .frame(maxWidth: .infinity)
                                .background(rowBackgroundColor)
                                .cornerRadius(12)
                                
                            }
                            .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
                            
                            Spacer().frame(height: UIScreen.main.bounds.height/80)
                        }
                        
                        ForEach(workoutsViewModel.otherWorkouts, id: \.workout_id) {workout in
                            NavigationLink(destination: SingleWorkoutView(workout: workout)) {
                                VStack {
                                    Text(workout.name)
                                        .font(.title)
                                        .fontWeight(.black)
                                        .foregroundStyle(.primary)
                                        .foregroundColor(.black)
                                        .multilineTextAlignment(.center)
                                }
                                .padding(.vertical, 20)
                                .padding(.horizontal)
                                .frame(maxWidth: .infinity)
                                .background(rowBackgroundColor)
                                .cornerRadius(12)
                            }
                            .frame(maxWidth: UIScreen.main.bounds.width * 0.8)
                            
                            Spacer().frame(height: UIScreen.main.bounds.height/80)
                        }
                    }
                }
                .padding()
                .background(Color(.systemGroupedBackground))
                .scrollIndicators(.visible)
            }
        }
        .padding()
        .toolbar {
            ToolbarItem(placement: .principal) {
                VStack {
                    Text("WORKOUT PLAN")
                        .font(.title)
                        .fontWeight(.black)
                        .foregroundColor(Color.red)
                        .font(.subheadline)
                        .foregroundStyle(.primary)
                        .foregroundColor(.black)
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                NavigationLink(destination: WorkoutCreatorView()) {
                    Image(systemName: "plus.app")
                        .font(.system(size: UIScreen.main.bounds.width/20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
}

#Preview {
    WorkoutPlanView()
        .environmentObject(WebSocketManager.shared)
}
