//
//  Untitled.swift
//  PowerCoachFrontend
//
//  Created by Brian Jing on 8/9/25.
//

import Foundation

// A function is the correct place to put executable code.
func printAllTimezones() {
    // This property returns an array of all known timezone identifiers.
    // The list is extensive and includes all valid "Region/City" and "Abbreviation" formats.
    let allTimezones = TimeZone.knownTimeZoneIdentifiers

    // You can print the entire array to the console.
    print("Total timezones found: \(allTimezones.count)")
    print("---")
    print("List of all known timezone identifiers:")

    // Or, you can loop through the array to print each one on a new line.
    // This is useful for seeing the full list clearly.
    for timezone in allTimezones {
        print(timezone)
    }
}

// You can call this function from the command line.
// for example, from a button's action or a view's `onAppear` modifier.
// Uncomment the line below to run the function when this file is executed as a standalone script.
// printAllTimezones()
