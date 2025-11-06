//
//  PrePowerCoachView.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/24/25.
//

import SwiftUI

/// A struct that represents the pre-form-tracking screen for POWERCOACH.
struct PrePowerCoachView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    @EnvironmentObject var workoutsViewModel: WorkoutsViewModel //Env object is found by TYPE, not name, so it can have a diff name here.
    
    // A computed property to determine if the "Start" button should be disabled.
    // It checks if the selected exercise exists in the availableExercises array.
    private var isStartButtonDisabled: Bool {
        return !availableExercises.contains(workoutsViewModel.selectedPerformingExercise)
    }
    
    var body: some View {
        // Use a ZStack to layer the background and the content.
        ZStack {
            // Background color with an aggressive, dark gradient.
            LinearGradient(
                gradient: Gradient(colors: [Color(hex: "#0c0c0c"), Color(hex: "#222222")]),
                startPoint: .top,
                endPoint: .bottom
            )
            .edgesIgnoringSafeArea(.all)

            // Main content stack.
            VStack() {
                Spacer()
                Spacer()
                
                // The main app title.
                Text("POWERCOACH")
                    .font(.system(size: 40)) // Use .system(size: 40) for a custom font size.
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                    .shadow(color: Color.gray.opacity(0.3), radius: 5, x: 0, y: 5)
                
                Text("Track my form for ...")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .padding()
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
                
                Menu() {
                    ForEach(availableExercises, id: \.self) { exercise in
                        Button(action: {
                            DispatchQueue.main.async {
                                workoutsViewModel.selectedPerformingExercise = exercise
                            }
                        }) {
                            Text(exercise)
                        }
                    }
                } label: {
                    Text("\(workoutsViewModel.selectedPerformingExercise)")
                        .font(.title2)
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color(hex: "#1a4f8f")) // Dark blue color.
                        .cornerRadius(12)
                        .padding(.horizontal, 40)
                        .shadow(color: Color.black.opacity(0.2), radius: 10, x: 0, y: 10)
                }
                
                Button(action: {
                    webSocketManager.emit(event: "start_powercoach", with: [
                        "start_time": Date().timeIntervalSince1970,
                        "exercise": workoutsViewModel.selectedPerformingExercise
                    ])
                }) {
                    NavigationLink(destination: PowerCoachView(webSocketManager: WebSocketManager.shared)) {
                        Text("Start")
                            .font(.title2)
                            .foregroundColor(isStartButtonDisabled ? .gray : .white)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color(hex: isStartButtonDisabled ? "#3a3a3a" : "#1a4f8f"))
                            .cornerRadius(12)
                            .padding(.horizontal, 40)
                            .shadow(color: Color.black.opacity(0.2), radius: 10, x: 0, y: 10)
                    }
                }
                .disabled(isStartButtonDisabled)
                
                Spacer()
                Spacer()
                Spacer()
                Spacer()
            }
            .padding()
        }
    }
}

// A helper extension to create a Color from a hex string.
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
