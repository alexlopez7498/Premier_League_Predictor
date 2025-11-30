"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getTeamLogoUrl } from "@/utils/teamLogos";

interface Player {
  id: number;
  name: string;
  nation: string;
  position: string;
  age: number;
  matchesPlayed: number;
  starts: number;
  minutes: number;
  minutesPerMatch: number;
  goals: number;
  assists: number;
  goalsAndAssists: number;
  nonPenaltyGoals: number;
  penaltyGoals: number;
  penaltyAttempts: number;
  yellowCards: number;
  redCards: number;
  expectedGoals: number;
  expectedNonPenaltyGoals: number;
  expectedAssists: number;
  expectedNonPenaltyGoalsAndAssists: number;
  progressiveCarries: number;
  progessivePasses: number;
  progessivePassesReceived: number;
  goalsPer90: number;
  assistsPer90: number;
  goalsAndAssistsPer90: number;
  nonPenaltyGoalsPer90: number;
  nonPenaltyGoalsAndAssistsPer90: number;
  expectedGoalsPer90: number;
  expectedAssistsPer90: number;
  expectedGoalsAndAssistsPer90: number;
  expectedNonPenaltyGoalsPer90: number;
  expectedNonPenaltyGoalsAndAssistsPer90: number;
  team_name: string;
}

type SortField = 'name' | 'goals' | 'assists' | 'goalsAndAssists' | 'matchesPlayed' | 'goalsPer90' | 'assistsPer90';
type SortDirection = 'asc' | 'desc';

export default function PlayerStatsPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [filteredPlayers, setFilteredPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState<string>("all");
  const [selectedPosition, setSelectedPosition] = useState<string>("all");
  const [sortField, setSortField] = useState<SortField>('goals');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Filter out squad totals, opponent totals, and other aggregate rows
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

  const fetchPlayers = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/players/', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        // Filter out aggregate rows
        const individualPlayers = data.filter((p: Player) => isIndividualPlayer(p));
        setPlayers(individualPlayers);
        
        // Extract unique teams
        const uniqueTeams = Array.from(new Set(individualPlayers.map((p: Player) => p.team_name))).sort();
        setTeams(uniqueTeams as string[]);
      } else {
        console.error('Failed to fetch players:', response.status, await response.text());
        setPlayers([]);
      }
    } catch (error) {
      console.error('Error fetching players:', error);
      setPlayers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  // Filter and sort players
  useEffect(() => {
    let filtered = [...players];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(player =>
        player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.team_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by team
    if (selectedTeam !== "all") {
      filtered = filtered.filter(player => player.team_name === selectedTeam);
    }

    // Filter by position
    if (selectedPosition !== "all") {
      filtered = filtered.filter(player => player.position === selectedPosition);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'goals':
          aValue = a.goals;
          bValue = b.goals;
          break;
        case 'assists':
          aValue = a.assists;
          bValue = b.assists;
          break;
        case 'goalsAndAssists':
          aValue = a.goalsAndAssists;
          bValue = b.goalsAndAssists;
          break;
        case 'matchesPlayed':
          aValue = a.matchesPlayed;
          bValue = b.matchesPlayed;
          break;
        case 'goalsPer90':
          aValue = a.goalsPer90;
          bValue = b.goalsPer90;
          break;
        case 'assistsPer90':
          aValue = a.assistsPer90;
          bValue = b.assistsPer90;
          break;
        default:
          aValue = a.goals;
          bValue = b.goals;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      } else {
        return sortDirection === 'asc'
          ? (aValue as number) - (bValue as number)
          : (bValue as number) - (aValue as number);
      }
    });

    setFilteredPlayers(filtered);
  }, [players, searchTerm, selectedTeam, selectedPosition, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const getPositionOptions = (): string[] => {
    const positions = Array.from(new Set(players.map(p => p.position))).filter(Boolean).sort();
    return positions;
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <i className="fas fa-sort-up ml-1"></i>
    ) : (
      <i className="fas fa-sort-down ml-1"></i>
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
            <span className="text-blue-600"> Player Stats</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Comprehensive player statistics and performance metrics
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search
              </label>
              <input
                type="text"
                placeholder="Search by name or team..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Team Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Team
              </label>
              <select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Teams</option>
                {teams.map(team => (
                  <option key={team} value={team}>{team}</option>
                ))}
              </select>
            </div>

            {/* Position Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Position
              </label>
              <select
                value={selectedPosition}
                onChange={(e) => setSelectedPosition(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Positions</option>
                {getPositionOptions().map(position => (
                  <option key={position} value={position}>{position}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Players Table */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-500 dark:text-gray-400">Loading players...</p>
            </div>
          ) : (
            <>
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Showing {filteredPlayers.length} of {players.length} players
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100 dark:bg-gray-700">
                    <tr>
                      <th 
                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600"
                        onClick={() => handleSort('name')}
                      >
                        Player <SortIcon field="name" />
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Team
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Pos
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        MP
                      </th>
                      <th 
                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600"
                        onClick={() => handleSort('goals')}
                      >
                        Goals <SortIcon field="goals" />
                      </th>
                      <th 
                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600"
                        onClick={() => handleSort('assists')}
                      >
                        Assists <SortIcon field="assists" />
                      </th>
                      <th 
                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600"
                        onClick={() => handleSort('goalsAndAssists')}
                      >
                        G+A <SortIcon field="goalsAndAssists" />
                      </th>
                      <th 
                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600"
                        onClick={() => handleSort('goalsPer90')}
                      >
                        G/90 <SortIcon field="goalsPer90" />
                      </th>
                      <th 
                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600"
                        onClick={() => handleSort('assistsPer90')}
                      >
                        A/90 <SortIcon field="assistsPer90" />
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        xG
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        xA
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {filteredPlayers.length > 0 ? (
                      filteredPlayers.map((player) => (
                        <tr
                          key={player.id}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors bg-white dark:bg-gray-800"
                        >
                          <td className="px-4 py-4 whitespace-nowrap">
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {player.name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {player.nation} • Age: {Math.floor(player.age)}
                            </div>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              {getTeamLogoUrl(player.team_name) && (
                                <Image
                                  src={getTeamLogoUrl(player.team_name)}
                                  alt={player.team_name}
                                  width={24}
                                  height={24}
                                  className="object-contain"
                                />
                              )}
                              <span className="text-sm text-gray-900 dark:text-white">
                                {player.team_name}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <span className="text-sm text-gray-900 dark:text-white">
                              {player.position}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                            {player.matchesPlayed}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center">
                            <span className="text-sm font-bold text-yellow-600 dark:text-yellow-400">
                              {player.goals}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center">
                            <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                              {player.assists}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center">
                            <span className="text-sm font-bold text-gray-900 dark:text-white">
                              {player.goalsAndAssists.toFixed(1)}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                            {player.goalsPer90.toFixed(2)}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                            {player.assistsPer90.toFixed(2)}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                            {player.expectedGoals.toFixed(2)}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 dark:text-white">
                            {player.expectedAssists.toFixed(2)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={11} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                          No players found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

