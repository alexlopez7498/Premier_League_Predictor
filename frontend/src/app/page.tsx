"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getTeamLogoUrl } from "@/utils/teamLogos";

interface Match {
  match_id: number;
  date: string;
  time: string;
  team_name: string;
  opponent: string;
  result: string;
  gf: number;
  ga: number;
}


export default function Home() {

  const [matches, setMatches] = useState<Match[]>([]);

  const sortMatchesByTime = (matchesToSort: Match[]): Match[] => {
    return [...matchesToSort].sort((a, b) => {
      // Parse date strings (YYYY-MM-DD format)
      const dateA = new Date(a.date).getTime();
      const dateB = new Date(b.date).getTime();
      
      // If dates are different, sort by date first
      if (dateA !== dateB) {
        return dateA - dateB;
      }
      
      // If dates are the same, sort by time
      const timeA = a.time ? parseInt(a.time.replace(':', '')) : 0;
      const timeB = b.time ? parseInt(b.time.replace(':', '')) : 0;
      return timeA - timeB;
    });
  };

  const fetchMatchForCurrentWeek = async () => {
    try 
    {
      // Get response from the API from the backend
      const response = await fetch('http://127.0.0.1:8000/matches/current-week',{
        method: 'GET',
        credentials: 'include',
      });
      // Check to see if the response returns data
      if (response.ok)
      {
        const data = await response.json();
        console.log('Fetched reports:', data);
        const sortedMatches = sortMatchesByTime(data);
        setMatches(sortedMatches);
      }
      else 
      {
        console.error('Failed to fetch reports:', response.status, await response.text());
      }
    } 
    catch (error) {
      console.error('Error fetching reports:', error);
    }
  }

  useEffect(() => {
    fetchMatchForCurrentWeek();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation Bar */}
      <Navbar />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
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
          <div className="space-y-8">
            {matches && matches.length > 0 ? (
              (() => {
                // Group matches by date
                const groupedByDate: Record<string, Match[]> = {};
                matches.forEach(match => {
                  if (!groupedByDate[match.date]) {
                    groupedByDate[match.date] = [];
                  }
                  groupedByDate[match.date].push(match);
                });

                // Sort dates and render
                return Object.entries(groupedByDate)
                  .sort(([dateA], [dateB]) => new Date(dateA).getTime() - new Date(dateB).getTime())
                  .map(([date, dayMatches]) => {
                    const [year, month, day] = date.split('-').map(Number);
                    const dateObj = new Date(Date.UTC(year, month - 1, day));
                    const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long', timeZone: 'UTC' });
                    const formattedDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
                    
                    return (
                      <div key={date} className="border-l-4 border-blue-600 pl-4">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                          {dayName}, {formattedDate}
                        </h3>
                        <div className="space-y-3">
                          {dayMatches.map((match, index) => (
                            <Link
                              key={match.match_id || index}
                              href={`/matches/${match.match_id}`}
                              className="block"
                            >
                              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg gap-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer">
                                <div className="flex items-center space-x-4 flex-1">
                                  <div className="w-12 h-12 flex-shrink-0 flex items-center justify-center">
                                    {getTeamLogoUrl(match.team_name) && (
                                      <Image 
                                        src={getTeamLogoUrl(match.team_name)} 
                                        alt={match.team_name} 
                                        width={40} 
                                        height={40}
                                        className="object-contain w-auto h-auto max-w-full max-h-full"
                                      />
                                    )}
                                    {!getTeamLogoUrl(match.team_name) && (
                                      <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                                    )}
                                  </div>
                                  <div className="text-right w-32 flex-shrink-0">
                                    <p className="font-semibold text-gray-900 dark:text-white text-sm">{match.team_name}</p>
                                  </div>
                                </div>
                                <div className="text-center flex-1">
                                  <p className="text-xs text-gray-500 dark:text-gray-400">{match.time}</p>
                                  {match.result && match.result !== "nan" && match.result !== "" ? (
                                    <div className="flex items-center justify-center space-x-2">
                                      <span className="text-lg font-bold text-gray-900 dark:text-white">
                                        {match.gf}
                                      </span>
                                      <span className="text-gray-500 dark:text-gray-400">-</span>
                                      <span className="text-lg font-bold text-gray-900 dark:text-white">
                                        {match.ga}
                                      </span>
                                    </div>
                                  ) : (
                                    <p className="font-medium text-gray-900 dark:text-white">VS</p>
                                  )}
                                </div>
                                <div className="flex items-center space-x-4 flex-1 justify-end">
                                  <div className="text-left w-32 flex-shrink-0">
                                    <p className="font-semibold text-gray-900 dark:text-white text-sm">{match.opponent}</p>
                                  </div>
                                  <div className="w-12 h-12 flex-shrink-0 flex items-center justify-center">
                                    {getTeamLogoUrl(match.opponent) && (
                                      <Image 
                                        src={getTeamLogoUrl(match.opponent)} 
                                        alt={match.opponent} 
                                        width={40} 
                                        height={40}
                                        className="object-contain w-auto h-auto max-w-full max-h-full"
                                      />
                                    )}
                                    {!getTeamLogoUrl(match.opponent) && (
                                      <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    );
                  });
              })()
            ) : (
              <p className="text-center text-gray-500 dark:text-gray-400">No matches found for this week</p>
            )}
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
      <Footer />
    </div>
  );
}