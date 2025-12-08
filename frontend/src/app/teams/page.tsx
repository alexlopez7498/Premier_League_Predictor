"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getTeamLogoUrl } from "@/utils/teamLogos";

interface Team {
  rank: number;
  name: string;
  matchesPlayed: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
  points: number;
  goalsPer90: number;
  expectedGoals: number;
  expectedGoalsAllowed: number;
  expectedGoalsDifference: number;
  expectedGoalsDifferencePer90: number;
  last5Wins: string;
  attendance: number;
  topTeamScorer: string;
  goalkeeper: string;
}

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

interface Player {
  id: number;
  name: string;
  nation: string;
  position: string;
  age: number;
  matchesPlayed: number;
  goals: number;
  assists: number;
  team_name: string;
}


export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [teamLast5Matches, setTeamLast5Matches] = useState<Record<string, Match[]>>({});
  const [players, setPlayers] = useState<Player[]>([]);
  const [topScorers, setTopScorers] = useState<Player[]>([]);
  const [topAssisters, setTopAssisters] = useState<Player[]>([]);

  const fetchTeams = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/teams/', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();

        // Sort teams by rank (1 at top, 20 at bottom)
        const sortedTeams = [...data].sort((a: Team, b: Team) => a.rank - b.rank);
        setTeams(sortedTeams);
      } else {
        console.error('Failed to fetch teams:', response.status, await response.text());
      }
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const fetchMatches = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/matches/', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setMatches(data);
        
        // get matches for each team to get last 5 for each team
        const matchesByTeam: Record<string, Match[]> = {};
        data.forEach((match: Match) => {
          if (!matchesByTeam[match.team_name]) {
            matchesByTeam[match.team_name] = [];
          }
          matchesByTeam[match.team_name].push(match);
        });

        // Sort matches by date (most recent first) and take last 5
        const last5ByTeam: Record<string, Match[]> = {};
        Object.keys(matchesByTeam).forEach((teamName) => {
          const teamMatches = matchesByTeam[teamName]
            .filter((m: Match) => m.result && m.result !== "nan" && m.result !== "")
            .sort((a: Match, b: Match) => {
              const dateA = new Date(a.date).getTime();
              const dateB = new Date(b.date).getTime();
              return dateB - dateA; // Most recent first
            })
            .slice(0, 5); // Get last 5 matches
          last5ByTeam[teamName] = teamMatches;
        });
        
        setTeamLast5Matches(last5ByTeam);
      } else {
        console.error('Failed to fetch matches:', response.status, await response.text());
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const fetchPlayers = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/players/', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlayers(data);
        
        const isIndividualPlayer = (player: Player): boolean => {
          if (!player.name || player.name.trim() === "") {
            return false;
          }
          const name = player.name.toLowerCase().trim();
          const excludedPatterns = [
            "squad total",
            "opponent total",
            "team total",
            "squad",
            "opponent"
          ];
          return !excludedPatterns.some(pattern => 
            name === pattern || 
            name.startsWith(pattern + " ") ||
            name.endsWith(" " + pattern)
          );
        };
        
        // Sort by goals (top scorers) - only individual players
        const scorers = [...data]
          .filter((p: Player) => isIndividualPlayer(p) && p.goals > 0)
          .sort((a: Player, b: Player) => b.goals - a.goals)
          .slice(0, 10);
        setTopScorers(scorers);
        
        // Sort by assists (top assisters) - only individual players
        const assisters = [...data]
          .filter((p: Player) => isIndividualPlayer(p) && p.assists > 0)
          .sort((a: Player, b: Player) => b.assists - a.assists)
          .slice(0, 10);
        setTopAssisters(assisters);
      } else {
        console.error('Failed to fetch players:', response.status, await response.text());
      }
    } catch (error) {
      console.error('Error fetching players:', error);
    }
  };

  useEffect(() => {
    fetchTeams();
    fetchMatches();
    fetchPlayers();
  }, []);

  // Determine result from match data
  const getMatchResult = (match: Match): "W" | "D" | "L" | null => {
    if (!match.result || match.result === "nan" || match.result === "") return null;
    
    // Check if result indicates win, draw, or loss
    if (match.result.includes("W")) return "W";
    if (match.result.includes("L")) return "L";
    if (match.result.includes("D")) return "D";
    
    return null;
  };

  // Format last 5 matches as circles with opponent logos
  const formatLast5Matches = (teamName: string) => {
    const last5 = teamLast5Matches[teamName] || [];
    
    if (last5.length === 0) {
      return <span className="text-gray-400">—</span>;
    }

    return (
      <div className="flex items-center justify-center space-x-1">
        {last5.map((match, index) => {
          const result = getMatchResult(match);
          let bgColor = "bg-gray-400";
          if (result === "W") bgColor = "bg-green-500";
          if (result === "D") bgColor = "bg-yellow-500";
          if (result === "L") bgColor = "bg-red-500";

          const opponentLogo = getTeamLogoUrl(match.opponent);

          return (
            <div
              key={match.match_id || index}
              className={`w-8 h-8 rounded-full ${bgColor} flex items-center justify-center border-2 border-white dark:border-gray-700 shadow-sm`}
              title={`${match.opponent} - ${result || "N/A"}`}
            >
              {opponentLogo ? (
                <Image
                  src={opponentLogo}
                  alt={match.opponent}
                  width={20}
                  height={20}
                  className="object-contain w-5 h-5"
                />
              ) : (
                <span className="text-white text-xs font-bold">
                  {match.opponent.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
          );
        })}
        {/* Fill remaining slots if less than 5 matches */}
        {Array.from({ length: Math.max(0, 5 - last5.length) }).map((_, i) => (
          <div
            key={`empty-${i}`}
            className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 border-2 border-white dark:border-gray-700"
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation Bar */}
      <Navbar />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Premier League
            <span className="text-blue-600"> Standings</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Current season team statistics and rankings
          </p>
        </div>

        {/* Teams Table */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Team
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    MP
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    W
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    D
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    L
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    GF
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    GA
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    GD
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Pts
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Last 5
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {teams && teams.length > 0 ? (
                  teams.map((team) => (
                    <tr
                      key={team.name}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors bg-white dark:bg-gray-800"
                    >
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-sm font-bold text-gray-900 dark:text-white">
                            {team.rank}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
                            {getTeamLogoUrl(team.name) ? (
                              <Image
                                src={getTeamLogoUrl(team.name)}
                                alt={team.name}
                                width={40}
                                height={40}
                                className="object-contain w-auto h-auto max-w-full max-h-full"
                              />
                            ) : (
                              <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                            )}
                          </div>
                          <Link href={`/teams/${encodeURIComponent(team.name)}`}>
                            <div className="text-sm font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                              {team.name}
                            </div>
                          </Link>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                        {team.matchesPlayed}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                        {team.wins}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                        {team.draws}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                        {team.losses}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                        {team.goalsFor}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                        {team.goalsAgainst}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-sm font-semibold text-gray-900 dark:text-white">
                        {team.goalDifference > 0 ? "+" : ""}{team.goalDifference}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                          {team.points}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center">
                        {formatLast5Matches(team.name)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={11} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                      No teams data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Scorers and Top Assisters Section */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Scorers */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gray-100 dark:bg-gray-700 px-6 py-4">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                <i className="fas fa-futbol mr-3"></i>
                Top Scorers
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Player
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Goals
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Matches
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {topScorers.length > 0 ? (
                    topScorers.map((player, index) => (
                      <tr
                        key={player.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors bg-white dark:bg-gray-800"
                      >
                        <td className="px-4 py-4 whitespace-nowrap">
                          <span className="text-sm font-bold text-gray-900 dark:text-white">
                            {index + 1}
                          </span>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
                              {getTeamLogoUrl(player.team_name) ? (
                                <Image
                                  src={getTeamLogoUrl(player.team_name)}
                                  alt={player.team_name}
                                  width={40}
                                  height={40}
                                  className="object-contain w-10 h-10"
                                />
                              ) : (
                                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded"></div>
                              )}
                            </div>
                            <div>
                              <div className="text-base font-bold text-gray-900 dark:text-white">
                                {player.name}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                {player.position} • {player.team_name}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <span className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                            {player.goals}
                          </span>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                          {player.matchesPlayed}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                        No scorers data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top Assisters */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gray-100 dark:bg-gray-700 px-6 py-4">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                <i className="fas fa-hand-holding-heart mr-3"></i>
                Top Assisters
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Player
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Assists
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Matches
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {topAssisters.length > 0 ? (
                    topAssisters.map((player, index) => (
                      <tr
                        key={player.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors bg-white dark:bg-gray-800"
                      >
                        <td className="px-4 py-4 whitespace-nowrap">
                          <span className="text-sm font-bold text-gray-900 dark:text-white">
                            {index + 1}
                          </span>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center">
                              {getTeamLogoUrl(player.team_name) ? (
                                <Image
                                  src={getTeamLogoUrl(player.team_name)}
                                  alt={player.team_name}
                                  width={40}
                                  height={40}
                                  className="object-contain w-10 h-10"
                                />
                              ) : (
                                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded"></div>
                              )}
                            </div>
                            <div>
                              <div className="text-base font-bold text-gray-900 dark:text-white">
                                {player.name}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                {player.position} • {player.team_name}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center">
                          <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                            {player.assists}
                          </span>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                          {player.matchesPlayed}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                        No assisters data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Additional Stats Section */}
        {teams && teams.length > 0 && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {teams.slice(0, 6).map((team) => (
              <div
                key={team.name}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
              >
                <div className="flex items-center space-x-3 mb-4">
                  {getTeamLogoUrl(team.name) && (
                    <Image
                      src={getTeamLogoUrl(team.name)}
                      alt={team.name}
                      width={40}
                      height={40}
                      className="object-contain"
                    />
                  )}
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    {team.name}
                  </h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Top Scorer:</span>
                    <span className="text-gray-900 dark:text-white font-semibold">
                      {team.topTeamScorer || "—"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Goalkeeper:</span>
                    <span className="text-gray-900 dark:text-white font-semibold">
                      {team.goalkeeper || "—"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Goals For:</span>
                    <span className="text-gray-900 dark:text-white font-semibold">
                      {team.goalsFor.toFixed(0)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Goals Against:</span>
                    <span className="text-gray-900 dark:text-white font-semibold">
                      {team.goalsAgainst.toFixed(0)}
                    </span>
                  </div>
                  {team.attendance > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Attendance:</span>
                      <span className="text-gray-900 dark:text-white font-semibold">
                        {team.attendance.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

