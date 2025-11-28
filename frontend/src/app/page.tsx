"use client"

import { useState } from "react";
import Navbar from "@/components/Navbar";

export default function Home() {
  const [activeTab, setActiveTab] = useState("home");

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation Bar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
            Premier League
            <span className="text-blue-600"> Predictor</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Predict match outcomes, analyze team performance, and track player statistics with our advanced AI-powered prediction engine.
          </p>
        </div>

        {/* Upcoming Matches */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Upcoming Featured Matches
          </h2>
          <div className="space-y-4">
            {[
              { home: "Manchester City", away: "Liverpool", date: "Tomorrow, 15:00" },
              { home: "Arsenal", away: "Chelsea", date: "Saturday, 12:30" },
              { home: "Manchester United", away: "Tottenham", date: "Sunday, 16:30" }
            ].map((match, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="text-right w-24">
                    <p className="font-semibold text-gray-900 dark:text-white">{match.home}</p>
                  </div>
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">{match.date}</p>
                  <p className="font-medium text-gray-900 dark:text-white">VS</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                  <div className="text-left w-24">
                    <p className="font-semibold text-gray-900 dark:text-white">{match.away}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors mb-4">
            Start Predicting Now
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <span className="text-lg font-bold text-gray-900 dark:text-white">
              </span>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="#" className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <i className="fab fa-facebook"></i>
              </a>
              <a href="#" className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <i className="fab fa-instagram"></i>
              </a>
            </div>
          </div>
          <div className="mt-4 text-center md:text-left">
            <p className="text-gray-500 dark:text-gray-400">
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}