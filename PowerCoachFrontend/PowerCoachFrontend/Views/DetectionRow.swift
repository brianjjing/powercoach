//
//  DetectionRow.swift
//  PowerCoachPrototype
//
//  Created by Brian Jing on 2/15/25.
//

import SwiftUI


struct DetectionRow: View {
    var inputDetection: ImageFeed
    
    var body: some View {
        HStack {
            Text(inputDetection.jsonData)
        }
    }
}

#Preview {
    Group {
    }
}
