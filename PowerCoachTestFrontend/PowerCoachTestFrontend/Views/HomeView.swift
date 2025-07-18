//
//  HomeView.swift
//  PowerCoachTestFrontend
//
//  Created by Brian Jing on 7/17/25.
//


import SwiftUI

struct HomeView: View {
    @EnvironmentObject var webSocketManager: WebSocketManager
    
    var body: some View {
//        Text("Change this to the coach speaking:")
//            .font(.largeTitle)
//            .fontWeight(.black)
//            .foregroundColor(Color.red)
//            .font(.subheadline)
//            .foregroundStyle(.secondary)
//            .foregroundColor(.black)
        CircleCoach()
        VStack(alignment: .center) {
            Text("\(webSocketManager.homeDisplay)")
                .font(.title)
                .fontWeight(.black)
                .foregroundColor(Color.red)
                .foregroundStyle(.secondary)
                .foregroundColor(.black)
                .multilineTextAlignment(.center)
        }
        .padding()
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("POWERCOACH")
                    .font(.title)
                    .fontWeight(.black)
                    .foregroundColor(Color.red)
                    .foregroundStyle(.secondary)
                    .foregroundColor(.black)
            }
            ToolbarItem(placement: .topBarTrailing) {
                //Make this a button later
                Image(systemName: "bell")
                    .font(.system(size: UIScreen.main.bounds.width/20))
                    .foregroundColor(.white)
            }
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(WebSocketManager.shared)
}
