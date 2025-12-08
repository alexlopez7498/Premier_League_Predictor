"use client";

import React, { useEffect, useMemo, useState, use } from "react";
import Link from "next/link";
import Image from "next/image";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getTeamLogoUrl } from "@/utils/teamLogos";
import { useRouter } from "next/navigation";

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
    "opponent",
  ];
  return !excludedPatterns.some(
    (pattern) =>
      name === pattern ||
      name.startsWith(pattern + " ") ||
      name.endsWith(" " + pattern)
  );
};

const formatDate = (value: string) => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const formatMatchResult = (match: Match) => {
  if (!match.result || match.result === "nan" || match.result === "") {
    return { label: "N/A", color: "bg-gray-400" };
  }
  if (match.result.includes("W")) return { label: "W", color: "bg-green-500" };
  if (match.result.includes("L")) return { label: "L", color: "bg-red-500" };
  if (match.result.includes("D")) return { label: "D", color: "bg-yellow-500" };
  return { label: "N/A", color: "bg-gray-400" };
};

export default function TeamDetailPage({
  params,
}: {
  params: Promise<{ team: string }>;
}) {
  const router = useRouter();
  const resolvedParams = use(params);
  const teamParam = decodeURIComponent(resolvedParams.team);
  const teamKey = teamParam.toLowerCase();

  const [team, setTeam] = useState<Team | null>(null);
  const [teamMatches, setTeamMatches] = useState<Match[]>([]);
  const [teamPlayers, setTeamPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [teamsRes, matchesRes, playersRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/teams/", {
            method: "GET",
            credentials: "include",
          }),
          fetch("http://127.0.0.1:8000/matches/", {
            method: "GET",
            credentials: "include",
          }),
          fetch("http://127.0.0.1:8000/players/", {
            method: "GET",
            credentials: "include",
          }),
        ]);

        if (!teamsRes.ok || !matchesRes.ok || !playersRes.ok) {
          const msg = `Failed to load data (${teamsRes.status}/${matchesRes.status}/${playersRes.status})`;
          throw new Error(msg);
        }

        const [teamsData, matchesData, playersData] = await Promise.all([
          teamsRes.json(),
          matchesRes.json(),
          playersRes.json(),
        ]);

        const currentTeam: Team | undefined = teamsData.find(
          (t: Team) => t.name.toLowerCase() === teamKey
        );

        if (!currentTeam) {
          setError("Team not found");
          setTeam(null);
        } else {
          setTeam(currentTeam);
        }

        const now = Date.now();
        const validTeamMatches: Match[] = matchesData.filter((m: Match) => {
          const isTeamMatch =
            m.team_name && m.team_name.toLowerCase() === teamKey;
          if (!isTeamMatch || !m.date) return false;
          const ts = new Date(m.date).getTime();
          return !Number.isNaN(ts);
        });

        const chronMatches = validTeamMatches.sort(
          (a: Match, b: Match) =>
            new Date(a.date).getTime() - new Date(b.date).getTime()
        );

        setTeamMatches(chronMatches);

        const filteredPlayers: Player[] = playersData
          .filter(
            (p: Player) =>
              p.team_name && p.team_name.toLowerCase() === teamKey
          )
          .filter(isIndividualPlayer);
        setTeamPlayers(filteredPlayers);
      } catch (err: any) {
        setError(err?.message || "Unable to load team data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [teamKey]);

  const topScorers = useMemo(
    () =>
      [...teamPlayers]
        .filter((p) => p.goals > 0)
        .sort((a, b) => b.goals - a.goals)
        .slice(0, 5),
    [teamPlayers]
  );

  const topAssisters = useMemo(
    () =>
      [...teamPlayers]
        .filter((p) => p.assists > 0)
        .sort((a, b) => b.assists - a.assists)
        .slice(0, 5),
    [teamPlayers]
  );
  const nowTs = useMemo(() => Date.now(), []);
  const orderedMatches = useMemo(() => {
    return [...teamMatches];
  }, [teamMatches]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
        <Navbar />
        <main className="max-w-6xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
          <p className="text-gray-700 dark:text-gray-200">Loading team data...</p>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
        <Navbar />
        <main className="max-w-6xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {error || "Team not found"}
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              We could not load information for "{teamParam}".
            </p>
            <button
              type="button"
              onClick={() => {
                if (typeof window !== "undefined" && window.history.length > 1) {
                  router.back();
                } else {
                  router.push("/teams");
                }
              }}
              className="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              ← Back
            </button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
      <Navbar />

      <main className="max-w-6xl mx-auto py-10 px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Breadcrumb / Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <button
              type="button"
              onClick={() => {
                if (typeof window !== "undefined" && window.history.length > 1) {
                  router.back();
                } else {
                  router.push("/teams");
                }
              }}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              ← Back
            </button>
            <div className="flex items-center space-x-3">
              {getTeamLogoUrl(team.name) && (
                <Image
                  src={getTeamLogoUrl(team.name)}
                  alt={team.name}
                  width={56}
                  height={56}
                  className="object-contain w-14 h-14"
                />
              )}
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {team.name}
                </h1>
                <p className="text-gray-600 dark:text-gray-300">
                  Rank #{team.rank} • {team.points} pts
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow px-4 py-3">
            <div className="text-sm text-gray-500 dark:text-gray-400">Record</div>
            <div className="text-xl font-semibold text-gray-900 dark:text-white">
              {team.wins}W - {team.draws}D - {team.losses}L
            </div>
          </div>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">Points</div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {team.points}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">Goal Diff</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {team.goalDifference > 0 ? "+" : ""}
              {team.goalDifference}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">GF / GA</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {team.goalsFor} / {team.goalsAgainst}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              xG / xGA
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {team.expectedGoals?.toFixed(1) ?? "—"} /{" "}
              {team.expectedGoalsAllowed?.toFixed(1) ?? "—"}
            </div>
          </div>
        </div>

        {/* Key figures */}
        <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Team Info
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Matches</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {team.matchesPlayed}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Goals/90</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {team.goalsPer90?.toFixed(2) ?? "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Top Scorer</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {team.topTeamScorer || "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Goalkeeper</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {team.goalkeeper || "—"}
                </span>
              </div>
              {team.attendance > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Attendance</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {team.attendance.toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Players */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
            <div className="px-6 py-4 bg-gray-100 dark:bg-gray-700">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Top Scorers
              </h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {topScorers.length === 0 && (
                <div className="px-6 py-4 text-gray-600 dark:text-gray-300">
                  No scorers recorded.
                </div>
              )}
              {topScorers.map((player) => (
                <div
                  key={player.id}
                  className="px-6 py-4 flex items-center justify-between"
                >
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {player.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {player.position} • {player.matchesPlayed} matches
                    </div>
                  </div>
                  <div className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                    {player.goals}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
            <div className="px-6 py-4 bg-gray-100 dark:bg-gray-700">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Top Assisters
              </h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {topAssisters.length === 0 && (
                <div className="px-6 py-4 text-gray-600 dark:text-gray-300">
                  No assist data recorded.
                </div>
              )}
              {topAssisters.map((player) => (
                <div
                  key={player.id}
                  className="px-6 py-4 flex items-center justify-between"
                >
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {player.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {player.position} • {player.matchesPlayed} matches
                    </div>
                  </div>
                  <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {player.assists}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* All matches table */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
          <div className="px-6 py-4 bg-gray-100 dark:bg-gray-700">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              Matches (season)
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
              Ordered oldest to newest • scroll for more
            </p>
          </div>
          <div className="overflow-x-auto">
            <div className="max-h-[620px] overflow-y-auto rounded-b-xl">
              <table className="w-full">
                <thead className="bg-gray-100 dark:bg-gray-700 sticky top-0 z-10">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Opponent
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Venue
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Result
                  </th>
                </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {orderedMatches.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-4 py-6 text-center text-gray-600 dark:text-gray-300"
                    >
                      No matches available.
                    </td>
                  </tr>
                )}
                {orderedMatches.map((match) => {
                  const { label, color } = formatMatchResult(match);
                  const matchTs = new Date(match.date).getTime();
                  const isFuture = !Number.isNaN(matchTs) && matchTs > nowTs;
                  return (
                    <tr key={match.match_id}>
                      <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                        {formatDate(match.date)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 dark:text-white flex items-center space-x-2">
                        {getTeamLogoUrl(match.opponent) && (
                          <Image
                            src={getTeamLogoUrl(match.opponent)}
                            alt={match.opponent}
                            width={24}
                            height={24}
                            className="object-contain w-6 h-6"
                          />
                        )}
                        <span>{match.opponent}</span>
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-gray-700 dark:text-gray-300">
                        {match.venue || "—"}
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-gray-900 dark:text-white font-semibold">
                        {match.gf} - {match.ga}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full text-white ${color}`}
                        >
                          {label}
                        </span>
                        {isFuture && (
                          <span className="ml-2 text-xs text-blue-600 dark:text-blue-400 font-semibold">
                            Upcoming
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
