SELECT 
 d.match_id, 
 d.innings_number,
 batting_team,
 over_number,
 ball_number, 
 runs_total, 
 has_wicket,
 SUM(runs_total) OVER (ORDER BY d.match_id, d.innings_number, over_number, ball_number ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS runs_running_total,
 SUM(has_wicket) OVER (ORDER BY d.match_id, d.innings_number, over_number, ball_number ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS wickets_running_total
FROM matches m
INNER JOIN innings i
ON m.id = i.match_id
INNER JOIN deliveries d
ON m.id = d.match_id
AND i.innings_number = d.innings_number