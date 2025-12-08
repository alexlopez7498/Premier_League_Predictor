"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
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
  xg: number;
  xga: number;
  poss: number;
  attendance: number;
  captain: string;
  formation: string;
  oppFormation: string;
  referee: string;
}

interface PredictionResult {
  home_team: string;
  away_team: string;
  home_win_prob: number;
  draw_prob: number;
  away_win_prob: number;
  predicted_score: string;
  prediction: string;
  confidence: number;
  accuracy: number;
  precision: number;
}

export default function MatchDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const matchId = params?.matchId ? parseInt(params.matchId as string) : null;
  const weekParam = searchParams.get('week');
  const backToMatchesUrl = weekParam ? `/matches?week=${weekParam}` : '/matches';
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) {
      setError("Invalid match ID");
      setLoading(false);
      return;
    }

    const fetchMatch = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:8000/matches/${matchId}`, {
          method: 'GET',
          credentials: 'include',
        });
        
        if (response.ok) {
          const data = await response.json();
          setMatch(data);
        } else {
          setError("Match not found");
        }
      } catch (error) {
        console.error('Error fetching match:', error);
        setError("Failed to load match");
      } finally {
        setLoading(false);
      }
    };

    fetchMatch();
  }, [matchId]);

  const formatDate = (dateString: string) => {
    const [year, month, day] = dateString.split('-').map(Number);
    const dateObj = new Date(Date.UTC(year, month - 1, day));
    return dateObj.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      timeZone: 'UTC' 
    });
  };

  const getResultColor = (result: string) => {
    if (!result || result === "nan" || result === "") return "text-gray-500";
    if (result.includes("W")) return "text-green-600";
    if (result.includes("L")) return "text-red-600";
    if (result.includes("D")) return "text-yellow-600";
    return "text-gray-500";
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;

  const handlePredictMatch = async () => {
    if (!match) return;
    setPredictionError(null);
    setPredictionLoading(true);

    const payload = {
      date: match.date,
      time: match.time || "",
      round: match.round || "",
      day: match.day || "",
      venue: match.venue || "",
      result: match.result || "nan",
      gf: match.gf ?? 0,
      ga: match.ga ?? 0,
      opponent: match.opponent,
      xg: match.xg ?? 0,
      xga: match.xga ?? 0,
      poss: match.poss ?? 0,
      attendance: match.attendance ?? 0,
      captain: match.captain || "",
      formation: match.formation || "",
      oppFormation: match.oppFormation || "",
      referee: match.referee || "",
      team_name: match.team_name,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/predict/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to generate prediction");
      }

      const data = await response.json();
      setPrediction(data);
    } catch (err: any) {
      console.error("Error predicting match:", err);
      setPrediction(null);
      setPredictionError(err?.message || "Failed to generate prediction");
    } finally {
      setPredictionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
        <Navbar />
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-500 dark:text-gray-400">Loading match details...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !match) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
        <Navbar />
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-red-500 dark:text-red-400 text-lg mb-4">{error || "Match not found"}</p>
            <Link
              href={backToMatchesUrl}
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              ← Back to Matches
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 dark:from-gray-900 dark:to-gray-800">
      <Navbar />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Link
          href={backToMatchesUrl}
          className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 mb-6"
        >
          <i className="fas fa-arrow-left mr-2"></i>
          Back to Matches
        </Link>

        {/* Match Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="text-center mb-6">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
              {match.round} • {formatDate(match.date)}
            </p>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Match Details
            </h1>
            {match.time && (
              <p className="text-lg text-gray-600 dark:text-gray-300">
                {match.time}
              </p>
            )}
          </div>

          {/* Match Score */}
          <div className="flex items-center justify-center gap-8 mb-8">
            {/* Home Team */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-24 h-24 flex items-center justify-center mb-4">
                {getTeamLogoUrl(match.team_name) ? (
                  <Image
                    src={getTeamLogoUrl(match.team_name)}
                    alt={match.team_name}
                    width={96}
                    height={96}
                    className="object-contain w-24 h-24"
                  />
                ) : (
                  <div className="w-24 h-24 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                )}
              </div>  
              <Link href={`/teams/${encodeURIComponent(match.team_name)}`}>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white text-center mb-2 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                  {match.team_name}
                </h2>
              </Link>
              {match.result && match.result !== "nan" && match.result !== "" ? (
                <div className="text-4xl font-bold text-gray-900 dark:text-white">
                  {match.gf}
                </div>
              ) : null}
            </div>

            {/* VS / Score */}
            <div className="flex flex-col items-center">
              {match.result && match.result !== "nan" && match.result !== "" ? (
                <>
                  <div className="text-5xl font-bold text-gray-900 dark:text-white mb-2">
                    {match.gf} - {match.ga}
                  </div>
                </>
              ) : (
                <div className="text-3xl font-bold text-gray-500 dark:text-gray-400">
                  VS
                </div>
              )}
            </div>

            {/* Away Team */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-24 h-24 flex items-center justify-center mb-4">
                {getTeamLogoUrl(match.opponent) ? (
                  <Image
                    src={getTeamLogoUrl(match.opponent)}
                    alt={match.opponent}
                    width={96}
                    height={96}
                    className="object-contain w-24 h-24"
                  />
                ) : (
                  <div className="w-24 h-24 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                )}
              </div>
              <Link href={`/teams/${encodeURIComponent(match.opponent)}`}>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white text-center mb-2 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                  {match.opponent}
                </h2>
              </Link>
              {match.result && match.result !== "nan" && match.result !== "" ? (
                <div className="text-4xl font-bold text-gray-900 dark:text-white">
                  {match.ga}
                </div>
              ) : null}
            </div>
          </div>
        </div>

        {/* Prediction Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">AI Match Prediction</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Run our prediction model to estimate the outcome based on recent form.
              </p>
            </div>
            <button
              onClick={handlePredictMatch}
              disabled={predictionLoading}
              className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {predictionLoading ? (
                <>
                  <span className="inline-block w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Predicting...
                </>
              ) : (
                <>
                  <i className="fas fa-magic mr-2"></i>
                  Predict Match
                </>
              )}
            </button>
          </div>
          {predictionError && (
            <p className="mt-4 text-sm text-red-500 dark:text-red-400">{predictionError}</p>
          )}
          {prediction && (
            <div className="mt-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">Predicted Result</p>
                  <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                    {prediction.prediction}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {prediction.home_team} vs {prediction.away_team}
                  </p>
                </div>
                <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">Predicted Score</p>
                  <p className="text-2xl font-bold text-green-700 dark:text-green-300">
                    {prediction.predicted_score}
                  </p>
                </div>
                <div className="bg-purple-50 dark:bg-purple-900/30 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">Confidence</p>
                  <p className="text-2xl font-bold text-purple-700 dark:text-purple-300">
                    {formatPercentage(prediction.confidence)}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Model accuracy {formatPercentage(prediction.accuracy)} • precision {formatPercentage(prediction.precision)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/60 dark:bg-gray-900/40 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{prediction.home_team} Win</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatPercentage(prediction.home_win_prob)}
                  </p>
                </div>
                <div className="bg-white/60 dark:bg-gray-900/40 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Draw</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatPercentage(prediction.draw_prob)}
                  </p>
                </div>
                <div className="bg-white/60 dark:bg-gray-900/40 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{prediction.away_team} Win</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatPercentage(prediction.away_win_prob)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Match Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

          {/* Team Formations */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Formations
            </h3>
            <div className="space-y-3">
              {match.formation && match.formation !== "nan" && (
                <div>
                  <span className="text-gray-600 dark:text-gray-400">{match.team_name}:</span>
                  <span className="ml-2 text-gray-900 dark:text-white font-semibold">
                    {match.formation}
                  </span>
                </div>
              )}
              {match.oppFormation && match.oppFormation !== "nan" && (
                <div>
                  <span className="text-gray-600 dark:text-gray-400">{match.opponent}:</span>
                  <span className="ml-2 text-gray-900 dark:text-white font-semibold">
                    {match.oppFormation}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Match Statistics */}
        {(match.xg > 0 || match.xga > 0 || match.poss > 0) && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Match Statistics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {match.xg > 0 && (
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Expected Goals (xG)</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {match.xg.toFixed(2)}
                  </p>
                </div>
              )}
              {match.xga > 0 && (
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Expected Goals Against (xGA)</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {match.xga.toFixed(2)}
                  </p>
                </div>
              )}
              {match.poss > 0 && (
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Possession</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {match.poss.toFixed(1)}%
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}



