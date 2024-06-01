DROP TABLE IF EXISTS calendario;

CREATE TABLE calendario (
  dia DATE,
  hora TIME
);

INSERT INTO calendario (dia, hora)
SELECT
  dia_series::date,
  (time '08:00' + (interval_series * interval '30 minutes'))::time
FROM
  generate_series(CURRENT_DATE, '2024-12-31'::date, '1 day') AS dia_series,
  generate_series(0, 9) AS interval_series
UNION ALL
SELECT
  dia_series::date,
  (time '14:00' + (interval_series * interval '30 minutes'))::time
FROM
  generate_series(CURRENT_DATE, '2024-12-31'::date, '1 day') AS dia_series,
  generate_series(0, 9) AS interval_series;
