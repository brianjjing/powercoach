//
//  ContentView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 1/16/25.
//

import SwiftUI

struct ContentView: View {
    //@State changes the variable within a VIEW
    //The shared WebSocketManager, which is initialized in WebSocketManager, is set to webSocketManager. It is a ViewModel instance.
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var tabIcons: TabIcons
    
    var body: some View {
        NavigationStack {
            VStack() {
                Group {
                    switch tabIcons.currentTab {
                    case 1:
                        HomeView()
                    case 2:
                        WorkoutPlanView()
                    case 4:
                        ForumView() //Change to a forum
                    case 5:
                        ProfileView()
                    default:
                        HomeView()
                    }
                }
                
                Spacer()
                
                ZStack(alignment: .bottom) {
                    Divider().frame(height: UIScreen.main.bounds.width/6).background(Color.white)
                    
                    HStack(alignment: .bottom) {
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/20)
                        
                        Button {
                            DispatchQueue.main.async {
                                tabIcons.currentTab = 1
                                tabIcons.houseSystemName = "house.fill"
                                tabIcons.workoutPlannerSystemName = "long.text.page.and.pencil"
                                tabIcons.forumSystemName = "message"
                                tabIcons.profileSystemName = "person.crop.circle"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Image(systemName: tabIcons.houseSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/10)
                        
                        Button {
                            DispatchQueue.main.async {
                                tabIcons.currentTab = 2
                                tabIcons.houseSystemName = "house"
                                tabIcons.workoutPlannerSystemName = "long.text.page.and.pencil.fill"
                                tabIcons.forumSystemName = "message"
                                tabIcons.profileSystemName = "person.crop.circle"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Image(systemName: tabIcons.workoutPlannerSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer()
                        
                        NavigationLink {
                            PowerCoachView(webSocketManager: WebSocketManager.shared)
                        } label: {
                            VStack {
                                PowerCoachTabIcon()
                            }
                        }
                        
                        Spacer()
                        
                        Button {
                            DispatchQueue.main.async {
                                tabIcons.currentTab = 4
                                tabIcons.houseSystemName = "house"
                                tabIcons.workoutPlannerSystemName = "long.text.page.and.pencil"
                                tabIcons.forumSystemName = "message.fill"
                                tabIcons.profileSystemName = "person.crop.circle"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Image(systemName: tabIcons.forumSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/10)
                        
                        Button {
                            DispatchQueue.main.async {
                                tabIcons.currentTab = 5
                                tabIcons.houseSystemName = "house"
                                tabIcons.workoutPlannerSystemName = "long.text.page.and.pencil"
                                tabIcons.forumSystemName = "message"
                                tabIcons.profileSystemName = "person.crop.circle.fill"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Image(systemName: tabIcons.profileSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/20)
                    }
                }
                
            }
        }
        
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager.shared)
        .environmentObject(TabIcons.sharedTab)
}
