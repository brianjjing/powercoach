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
    @State var currentTab: Int = 1
    @State var houseSystemName = "house.fill"
    @State var workoutPlannerSystemName = "long.text.page.and.pencil"
    @State var forumSystemName = "message"
    @State var profileSystemName = "person.crop.circle"
    
    var body: some View {
        NavigationStack {
            VStack() {
                //Adapt the colors to the color scheme!!! (light mode vs dark mode)
                
                Group {
                    switch currentTab {
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
                                currentTab = 1
                                houseSystemName = "house.fill"
                                workoutPlannerSystemName = "long.text.page.and.pencil"
                                forumSystemName = "message"
                                profileSystemName = "person.crop.circle"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Spacer().frame(height: UIScreen.main.bounds.height/3)
                                Image(systemName: houseSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/10)
                        
                        Button {
                            DispatchQueue.main.async {
                                currentTab = 2
                                houseSystemName = "house"
                                workoutPlannerSystemName = "long.text.page.and.pencil.fill"
                                forumSystemName = "message"
                                profileSystemName = "person.crop.circle"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Spacer().frame(height: UIScreen.main.bounds.height/3)
                                Image(systemName: workoutPlannerSystemName)
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
                                currentTab = 4
                                houseSystemName = "house"
                                workoutPlannerSystemName = "long.text.page.and.pencil"
                                forumSystemName = "message.fill"
                                profileSystemName = "person.crop.circle"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Spacer().frame(height: UIScreen.main.bounds.height/3)
                                Image(systemName: forumSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/10)
                        
                        Button {
                            DispatchQueue.main.async {
                                currentTab = 5
                                houseSystemName = "house"
                                workoutPlannerSystemName = "long.text.page.and.pencil"
                                forumSystemName = "message"
                                profileSystemName = "person.crop.circle.fill"
                            }
                        } label: {
                            VStack (alignment: .center) {
                                Spacer().frame(height: UIScreen.main.bounds.height/3)
                                Image(systemName: profileSystemName)
                                    .resizable()
                                    .colorMultiply(Color.black)
                                    .frame(width: UIScreen.main.bounds.width/14, height: UIScreen.main.bounds.width/14)
                                Spacer().frame(height: UIScreen.main.bounds.width/21)
                            }
                        }
                        
                        Spacer().frame(width: UIScreen.main.bounds.width/20)
                    }
                    //Spacer().frame(height: UIScreen.main.bounds.height/50)
                }
                
            }
        }
        
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager.shared)
}
