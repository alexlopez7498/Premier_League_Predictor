"use client";

import React, { useState, useEffect, Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getTeamLogoUrl } from "@/utils/teamLogos";

interface Match {
  match_id: number;
  date: string;
  time: string;
  round: string;
  day: string;
  venue: string;
  result: string;
  gf: number;
  ga: number;
  opponent: string;
  team_name: string;
}

function MatchesContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [matches, setMatches] = useState<Match[]>([]);
  const [currentWeek, setCurrentWeek] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);


  // Extract week number from round string
  const extractWeekNumber = (round: string): number | null => {
    const match = round.match(/Matchweek\s+(\d+)/i);
    return match ? parseInt(match[1], 10) : null;
  };

  // Get current week from today's date
  const getCurrentWeekNumber = (): number => {
    const today = new Date();
    const startOfSeason = new Date(today.getFullYear(), 7, 1); 
    const daysDiff = Math.floor((today.getTime() - startOfSeason.getTime()) / (1000 * 60 * 60 * 24));
    const weekNumber = Math.floor(daysDiff / 7) + 1;
    return Math.max(1, Math.min(38, weekNumber)); // Premier League has 38 weeks
  };

  const fetchMatchesForWeek = async (weekNumber: number) => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/matches/Matchweek/${weekNumber}`, {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        // Sort matches by date and time
        const sortedMatches = [...data].sort((a: Match, b: Match) => {
          const dateA = new Date(a.date).getTime();
          const dateB = new Date(b.date).getTime();
          if (dateA !== dateB) {
            return dateA - dateB;
          }
          const timeA = a.time ? parseInt(a.time.replace(':', '')) : 0;
          const timeB = b.time ? parseInt(b.time.replace(':', '')) : 0;
          return timeA - timeB;
        });
        setMatches(sortedMatches);
      } else {
        console.error('Failed to fetch matches:', response.status, await response.text());
        setMatches([]);
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentWeekMatches = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/matches/current-week', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.length > 0) {
          // Extract week number from first match
          const weekNumber = extractWeekNumber(data[0].round);
          if (weekNumber) {
            setCurrentWeek(weekNumber);
            await fetchMatchesForWeek(weekNumber);
            // Update URL to reflect current week
            router.replace(`/matches?week=${weekNumber}`);
            return;
          }
        }
        // Fallback to calculating current week
        const weekNumber = getCurrentWeekNumber();
        setCurrentWeek(weekNumber);
        await fetchMatchesForWeek(weekNumber);
        router.replace(`/matches?week=${weekNumber}`);
      } else {
        // Fallback to calculating current week
        const weekNumber = getCurrentWeekNumber();
        setCurrentWeek(weekNumber);
        await fetchMatchesForWeek(weekNumber);
        router.replace(`/matches?week=${weekNumber}`);
      }
    } catch (error) {
      console.error('Error fetching current week matches:', error);
      // Fallback to calculating current week
      const weekNumber = getCurrentWeekNumber();
      setCurrentWeek(weekNumber);
      await fetchMatchesForWeek(weekNumber);
      router.replace(`/matches?week=${weekNumber}`);
    }
  };

  useEffect(() => {
    // Check if week is in URL params
    const weekParam = searchParams.get('week');
    if (weekParam) {
      const weekNumber = parseInt(weekParam, 10);
      if (weekNumber >= 1 && weekNumber <= 38) {
        setCurrentWeek(weekNumber);
        fetchMatchesForWeek(weekNumber);
        return;
      }
    }
    // Otherwise fetch current week (only if no week param exists)
    if (!weekParam) {
      fetchCurrentWeekMatches();
    }
  }, [searchParams]);

  const goToPreviousWeek = () => {
    if (currentWeek !== null && currentWeek > 1) {
      const newWeek = currentWeek - 1;
      setCurrentWeek(newWeek);
      fetchMatchesForWeek(newWeek);
      
      // Update URL with new week
      router.push(`/matches?week=${newWeek}`);
    }
  };

  const goToNextWeek = () => {
    if (currentWeek !== null && currentWeek < 38) {
      const newWeek = currentWeek + 1;
      setCurrentWeek(newWeek);
      fetchMatchesForWeek(newWeek);

      // Update URL with new week
      router.push(`/matches?week=${newWeek}`);
    }
  };

  // Group matches by date
  const groupMatchesByDate = (matchesToGroup: Match[]): Record<string, Match[]> => {
    const grouped: Record<string, Match[]> = {};
    matchesToGroup.forEach(match => {
      if (!grouped[match.date]) {
        grouped[match.date] = [];
      }
      grouped[match.date].push(match);
    });
    return grouped;
  };

  const groupedMatches = groupMatchesByDate(matches);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation Bar */}
      <Navbar />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Premier League
            <span className="text-blue-600"> Matches</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            View matches by week
          </p>
        </div>

        {/* Week Navigation */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <button
              onClick={goToPreviousWeek}
              disabled={currentWeek === null || currentWeek <= 1 || loading}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <i className="fas fa-chevron-left"></i>
              <span>Previous Week</span>
            </button>

            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {currentWeek !== null ? `Matchweek ${currentWeek}` : "Loading..."}
              </h2>
              {matches.length > 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {matches.length} {matches.length === 1 ? 'match' : 'matches'}
                </p>
              )}
            </div>

            <button
              onClick={goToNextWeek}
              disabled={currentWeek === null || currentWeek >= 38 || loading}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span>Next Week</span>
              <i className="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

        {/* Matches List */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-500 dark:text-gray-400">Loading matches...</p>
            </div>
          ) : matches.length > 0 ? (
            <div className="space-y-8">
              {Object.entries(groupedMatches)
                .sort(([dateA], [dateB]) => new Date(dateA).getTime() - new Date(dateB).getTime())
                .map(([date, dayMatches]) => {
                  const [year, month, day] = date.split('-').map(Number);
                  const dateObj = new Date(Date.UTC(year, month - 1, day));
                  const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long', timeZone: 'UTC' });
                  const formattedDate = dateObj.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric', 
                    year: 'numeric', 
                    timeZone: 'UTC' 
                  });
                  
                  return (
                    <div key={date} className="border-l-4 border-blue-600 pl-4">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        {dayName}, {formattedDate}
                      </h3>
                      <div className="space-y-3">
                        {dayMatches.map((match, index) => (
                          <Link
                            key={match.match_id || index}
                            href={`/matches/${match.match_id}${currentWeek !== null ? `?week=${currentWeek}` : ''}`}
                            className="block"
                          >
                            <div 
                              className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg gap-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                            >
                            <div className="flex items-center space-x-4 flex-1">
                              <div className="w-12 h-12 flex-shrink-0 flex items-center justify-center">
                                {getTeamLogoUrl(match.team_name) ? (
                                  <Image 
                                    src={getTeamLogoUrl(match.team_name)} 
                                    alt={match.team_name} 
                                    width={48} 
                                    height={48}
                                    className="object-contain w-12 h-12"
                                  />
                                ) : (
                                  <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                                )}
                              </div>
                              <div className="text-right w-32 flex-shrink-0">
                                <p className="font-semibold text-gray-900 dark:text-white text-sm">
                                  {match.team_name}
                                </p>
                              </div>
                            </div>
                            <div className="text-center flex-1">
                              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                                {match.time}
                              </p>
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
                              {match.venue && (
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  {match.venue}
                                </p>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 flex-1 justify-end">
                              <div className="text-left w-32 flex-shrink-0">
                                <p className="font-semibold text-gray-900 dark:text-white text-sm">
                                  {match.opponent}
                                </p>
                              </div>
                              <div className="w-12 h-12 flex-shrink-0 flex items-center justify-center">
                                {getTeamLogoUrl(match.opponent) ? (
                                  <Image 
                                    src={getTeamLogoUrl(match.opponent)} 
                                    alt={match.opponent} 
                                    width={48} 
                                    height={48}
                                    className="object-contain w-12 h-12"
                                  />
                                ) : (
                                  <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                                )}
                              </div>
                            </div>
                          </div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  );
                })}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400 text-lg">
                No matches found for this week
              </p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default function MatchesPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <MatchesContent />
    </Suspense>
  );
}

