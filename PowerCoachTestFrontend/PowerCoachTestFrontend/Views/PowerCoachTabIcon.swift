//
//  PowerCoachTabIcon.swift
//  PowerCoachTestFrontend
//
//  Created by Brian Jing on 7/12/25.
//

import SwiftUI

struct PowerCoachTabIcon: View {
    var body: some View {
        Image("powercoachlogo")
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
