//  HomeView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel //Env object is found by TYPE, not name, so it can have a diff name here.
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    var body: some View {
        VStack {
            if !workoutsViewModel.todaysWorkouts.isEmpty {
                Text(workoutsViewModel.homeDisplayMessage)
                    .font(.title)
                    .fontWeight(.bold)
                    .fontDesign(.rounded)
                    .foregroundStyle(.primary)
                    .foregroundColor(buttonTextColor)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
                
                //LET USER SET THE WORKOUT FOR TODAY DISPLAYED AS WELL!!! (can have multiple workouts for a day)
                if let todaysWorkout = workoutsViewModel.todaysWorkouts.first {
                    List {
                        // Items are already unique, so \.self is used.
                        ForEach(0..<todaysWorkout.num_exercises, id: \.self) {index in
                            Text("\(todaysWorkout.sets[index])x\(todaysWorkout.reps[index]) \(todaysWorkout.exercises[index])")
                                .font(.title3)
                                .fontWeight(.bold)
                                .foregroundStyle(.primary)
                        }
                    }
                    .listStyle(.insetGrouped)
                }
            } else {
                Text(workoutsViewModel.homeDisplayMessage)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundStyle(.primary)
                    .foregroundColor(buttonTextColor)
                    .multilineTextAlignment(.center)
                
                Spacer().frame(height: UIScreen.main.bounds.height/16)
                
                NavigationLink(destination: WorkoutCreatorView()) {
                    Text("Create a workout")
                        .padding()
                        .font(.title2)
                        .bold()
                        .background(Color(.systemGray6))
                        .foregroundStyle(buttonTextColor)
                        .cornerRadius(12)
                }
                
                Spacer().frame(height: UIScreen.main.bounds.height/20)
                
                //Button for one workout
                Button() {
                    //Go to the one workout creator
                    DispatchQueue.main.async {
                        tabIcons.currentTab = 0 //Make this for the one workout creator
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
                workoutsViewModel.displayCurrentWorkout()
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
                        .font(.system(size: UIScreen.main.bounds.width/20))
                        .foregroundColor(.primary)
                }
            }
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(WebSocketManager.shared)
        .environmentObject(TabIcons.sharedTab)
}
