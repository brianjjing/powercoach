//
//  CircleImage.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 2/15/25.
//

import SwiftUI

struct CircleImage: View {
    var body: some View {
        Image("dumbbell")
            .clipShape(Circle())
            .overlay {
                Circle().stroke(.white, lineWidth: 4)
            }
            .shadow(radius: 7)
    }
}

#Preview {
    CircleImage()
}
