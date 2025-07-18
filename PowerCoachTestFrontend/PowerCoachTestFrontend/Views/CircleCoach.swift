//
//  CircleCoach.swift
//  PowerCoachTestFrontend
//
//  Created by Brian Jing on 7/17/25.
//

import SwiftUI

//WILL NOT NEED THIS AT ALL.

struct CircleCoach: View {
    var body: some View {
        Image("powercoachlogo")
            .clipShape(Circle())
            .overlay {
                Circle().stroke(.white, lineWidth: 4)
            }
            .shadow(radius: 8)
    }
}

#Preview {
    CircleCoach()
}
