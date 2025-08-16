//  HomeView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel
    @Environment(\.colorScheme) var colorScheme
    
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    var rowBackgroundColor: Color {
        colorScheme == .light ? Color(.systemGray5) : Color(.systemGray4)
    }
    
    var body: some View {
        VStack {
            let todaysWorkout = workoutsViewModel.workouts.first(where: { $0.today == true }) //Also make it the one where not everything is completed
            
            if let todaysWorkout = todaysWorkout {
                // Content to display when a workout exists
                Text("Today's Workout: \(todaysWorkout.name)")
                    .font(.title)
                    .fontWeight(.bold)
                    .fontDesign(.rounded)
                    .foregroundStyle(buttonTextColor)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
                
                // ScrollView for the workout buttons.
                // Note: The structure here assumes you want a scrollable list of
                // 'today's workouts' and then show details of the first one below.
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(0..<todaysWorkout.exerciseNames.count, id: \.self) { index in
                            ExerciseDisplayRow(workout: todaysWorkout, index: index)
                        }
                    }
                }
                .padding()
                .background(Color(.systemGroupedBackground))
                .scrollIndicators(.visible)
            } else {
                // Content to display when no workouts are available
                Text(workoutsViewModel.homeDisplayMessage)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundStyle(buttonTextColor)
                    .multilineTextAlignment(.center)
                
                Spacer().frame(height: UIScreen.main.bounds.height / 16)
                
                NavigationLink(destination: WorkoutCreatorView()) {
                    Text("Create a workout")
                        .padding()
                        .font(.title2)
                        .bold()
                        .background(Color(.systemGray6))
                        .foregroundStyle(buttonTextColor)
                        .cornerRadius(12)
                }
                
                Spacer().frame(height: UIScreen.main.bounds.height / 20)
                
                // Button for one workout
                Button() {
                    // Go to the one workout creator
                    DispatchQueue.main.async {
                        tabIcons.currentTab = 0 // Make this for the one workout creator
                    }
                } label: {
                    Text("One-time workout")
                        .padding()
                        .font(.title2)
                        .bold()
                        .background(Color(.systemGray6))
                        .foregroundStyle(buttonTextColor)
                        .cornerRadius(12)
                }
            }
        }
        .padding()
        .onAppear() {
            DispatchQueue.main.async {
                workoutsViewModel.getWorkouts()
            }
        }
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("POWERCOACH")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .foregroundStyle(.primary)
            }
            ToolbarItem(placement: .topBarTrailing) {
                NavigationLink(destination: InProgressView()) {
                    Image(systemName: "bell")
                        .font(.system(size: UIScreen.main.bounds.width / 20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
}

// NOTE: This preview requires `WebSocketManager` and `TabIcons` to be defined
// For this example, we will just use a minimal preview environment.
#Preview {
    HomeView()
        .environmentObject(WebSocketManager.shared)
        .environmentObject(TabIcons.sharedTab)
        .environmentObject(WorkoutsViewModel())
}
