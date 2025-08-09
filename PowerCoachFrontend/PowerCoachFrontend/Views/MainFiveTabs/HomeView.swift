//  HomeView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//

import SwiftUI

struct HomeView: View {
    @StateObject var viewModel = HomeScreenViewModel()
    
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    var body: some View {
        VStack {
            if !viewModel.workouts.isEmpty {
                VStack {
                    Text(viewModel.homeDisplayMessage)
                        .font(.title2)
                        .fontWeight(.black)
                        .foregroundColor(Color.red)
                        .foregroundStyle(.primary)
                        .foregroundColor(.black)
                        .multilineTextAlignment(.center)
                    
                    //Will style the workout under it better:
                    // setting id: \. allows for tracking elements in the ForEach as a key path
                    if let todaysWorkout = viewModel.workouts.first {
                        List {
                            // Loop through the 'exercises' array of the first workout
                            ForEach(todaysWorkout.exercises, id: \.self) { exercise in
                                Text(exercise)
                                    .font(.title3)
                                    .foregroundColor(.primary)
                                    .listRowBackground(Color.clear)
                            }
                        }
                    }
                }
            } else {
                Text(viewModel.homeDisplayMessage)
                    .font(.title2)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
                    .multilineTextAlignment(.center)
                
                Spacer().frame(height: UIScreen.main.bounds.height/16)
                
                NavigationLink(destination: WorkoutCreatorView()) {
                    VStack {
                        Text("Create a workout")
                            .padding()
                            .font(.title2)
                            .bold()
                            .background(Color(.systemGray6))
                            .foregroundStyle(buttonTextColor)
                            .cornerRadius(12)
                    }
                }
                
                Spacer().frame(height: UIScreen.main.bounds.height/20)
                
                //Button for one workout
                Button() {
                    //Go to the one workout creator
                    DispatchQueue.main.async {
                        tabIcons.currentTab = 0 //Make this for the one workout creator
                    }
                } label: {
                    VStack {
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
        }
        .padding()
        .onAppear() {
            DispatchQueue.main.async {
                viewModel.displayCurrentWorkout()
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
