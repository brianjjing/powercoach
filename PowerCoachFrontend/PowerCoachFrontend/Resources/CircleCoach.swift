//
//  CircleImage.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 2/15/25.
//

import SwiftUI

//WILL NOT NEED THIS AT ALL.

struct CircleCoach: View {
    var body: some View {
        Image("powercoacholdlogo")
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
