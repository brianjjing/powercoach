//
//  PowerCoachTab.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 5/19/25.
//

import SwiftUI

class TabIcons: ObservableObject {
    static let sharedTab = TabIcons()
    
    @Published var currentTab: Int = 1
    
    @Published var houseSystemName = "house.fill"
    @Published var workoutPlannerSystemName = "long.text.page.and.pencil"
    @Published var forumSystemName = "message"
    @Published var profileSystemName = "person.crop.circle"
    
    init() {}
}

struct PowerCoachTabIcon: View {
    var body: some View {
        Image("powercoachnewlogo")
            .resizable()
            .frame(width: UIScreen.main.bounds.width/3.5, height: UIScreen.main.bounds.width/3.5) //Make this cropped better by copying the aspect ratio and downsizing dumbbell image
            .clipShape(Circle())
            .overlay {
                Circle().stroke(Color.red, lineWidth: 4)
            }
            .shadow(color: Color.red, radius: 8)
    }
}

#Preview {
    PowerCoachTabIcon()
}
