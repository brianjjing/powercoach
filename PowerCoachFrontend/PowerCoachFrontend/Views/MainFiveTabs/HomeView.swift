//  HomeView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 3/28/25.
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    @Environment(\.colorScheme) var colorScheme //Rerenders the variable and its views when the environment object changes, since it depends on it.
    // Changes button text color based on light or dark mode:
    var buttonTextColor: Color {
        colorScheme == .light ? .black : .white
    }
    
    var body: some View {
        VStack {
            if webSocketManager.currentWorkout != nil{
                VStack {
                    Text("TODAY'S WORKOUT: \(String(describing: webSocketManager.currentWorkout))")
                        .font(.title2)
                        .fontWeight(.black)
                        .foregroundColor(Color.red)
                        .foregroundStyle(.primary)
                        .foregroundColor(.black)
                        .multilineTextAlignment(.center)
                }
            } else {
                Text("You don't have a workout plan set yet!")
                    .font(.title2)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .foregroundStyle(.primary)
                    .foregroundColor(.black)
                    .multilineTextAlignment(.center)
                
                Spacer().frame(height: UIScreen.main.bounds.height/16)
                
                Button() {
                    DispatchQueue.main.async {
                        tabIcons.currentTab = 2
                        tabIcons.houseSystemName = "house"
                        tabIcons.workoutPlannerSystemName = "long.text.page.and.pencil.fill"
                        tabIcons.forumSystemName = "message"
                        tabIcons.profileSystemName = "person.crop.circle"
                    }
                } label: {
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
