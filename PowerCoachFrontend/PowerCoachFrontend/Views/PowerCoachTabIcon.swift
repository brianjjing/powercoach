//
//  PowerCoachTab.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 5/19/25.
//

import SwiftUI

struct PowerCoachTabIcon: View {
    var body: some View {
        Image("dumbbell")
            .clipShape(Circle())
            .overlay {
                Circle().stroke(Color.red, lineWidth: 6)
            }
            .shadow(color: Color.red, radius: 12)
    }
}

#Preview {
    PowerCoachTabIcon()
}
