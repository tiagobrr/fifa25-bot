class DataAnalyzer:
    def get_daily_stats(self, matches):
        return {"total_matches": len(matches)}
    
    def get_player_statistics(self, matches):
        players = {}
        for match in matches:
            player = match.get('player')
            if player:
                players[player] = players.get(player, 0) + 1
        return [{"player": p, "matches_played": c} for p, c in players.items()]
    
    def generate_excel_report(self, matches):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Matches"
        ws.append(["Player", "Team", "Opponent", "Goals", "Win", "League", "Stadium", "Date", "Time", "Status"])
        for match in matches:
            ws.append([
                match.get("player"),
                match.get("team"),
                match.get("opponent"),
                match.get("goals"),
                match.get("win"),
                match.get("league"),
                match.get("stadium"),
                match.get("date"),
                match.get("time"),
                match.get("status"),
            ])
        filename = "daily_report.xlsx"
        wb.save(filename)
        return filename
