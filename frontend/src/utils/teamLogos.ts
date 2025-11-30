// Team logo mapping utility
export const getTeamLogoUrl = (teamName: string): string => {
  const teamLogos: Record<string, string> = {
    "Manchester City": "https://resources.premierleague.com/premierleague25/badges-alt/43.svg",
    "Liverpool": "https://resources.premierleague.com/premierleague25/badges-alt/14.svg",
    "Arsenal": "https://resources.premierleague.com/premierleague25/badges-alt/3.svg",
    "Chelsea": "https://resources.premierleague.com/premierleague25/badges-alt/8.svg",
    "Manchester Utd": "https://resources.premierleague.com/premierleague25/badges-alt/1.svg",
    "Tottenham": "https://resources.premierleague.com/premierleague25/badges-alt/6.svg",
    "Brighton": "https://resources.premierleague.com/premierleague25/badges-alt/36.svg",
    "Aston Villa": "https://resources.premierleague.com/premierleague25/badges-alt/7.svg",
    "Newcastle Utd": "https://resources.premierleague.com/premierleague25/badges-alt/4.svg",
    "West Ham": "https://resources.premierleague.com/premierleague25/badges-alt/21.svg",
    "Wolves": "https://resources.premierleague.com/premierleague25/badges-alt/39.svg",
    "Nott'ham Forest": "https://resources.premierleague.com/premierleague25/badges-alt/17.svg",
    "Crystal Palace": "https://resources.premierleague.com/premierleague25/badges-alt/31.svg",
    "Fulham": "https://resources.premierleague.com/premierleague25/badges-alt/54.svg",
    "Everton": "https://resources.premierleague.com/premierleague25/badges-alt/11.svg",
    "Bournemouth": "https://resources.premierleague.com/premierleague25/badges-alt/91.svg",
    "Leeds United": "https://resources.premierleague.com/premierleague25/badges-alt/2.svg",
    "Brentford": "https://resources.premierleague.com/premierleague25/badges-alt/94.svg",
    "Burnley": "https://resources.premierleague.com/premierleague25/badges-alt/90.svg",
    "Sunderland": "https://resources.premierleague.com/premierleague25/badges-alt/56.svg"
  };
  return teamLogos[teamName] || "";
};


