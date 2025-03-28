//
//  Detection.swift
//  PowerCoachPrototype
//
//  Created by Brian Jing on 2/15/25.
//

import Foundation
import SwiftUI

//What to do now: Find out how to send the live message from the frame to the frontend.
//No need to show the bounding box!!! That's only for testing, using backend.

struct Connection: Codable {
    var sid: String
    var upgrades: [String]
    var pingTimeout: Int
    var pingInterval: Int
    var maxPayload: Int
}
