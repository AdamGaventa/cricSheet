SELECT batsman_name, match_id, innings_number, SUM(runs_batsman) as score FROM deliveries
GROUP BY batsman_name, match_id, innings_number
ORDER BY match_id DESC, innings_number ASC, score DESC