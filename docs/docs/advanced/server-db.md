---
title: Server database
sidebar_label: Server database
---

Reporting server uses embedded SQLite3 database for storage - the database file can be found in server data directory and is named `gullveig.sqlite3`.

You can manipulate this database freely using SQLite3 command line tools.

## Database backups

To back up reporting server database you must use SQLite3 command line tool - see [https://www.sqlite.org/cli.html](https://www.sqlite.org/cli.html) for more information. 

## Data retention

Gullveig server periodically compacts the database and permanently deletes old data. Data is deleted after retention period for the particular data unit has passed, as shown bellow.

| Data table             | Retention                 |
|------------------------|---------------------------|
| Metrics by second      | 1 hour                    |
| Metrics by minute      | 24 hours                  |
| Metrics by hour        | 7 days                    |
| Metrics by day         | 3 months                  |
| Metrics by week        | 6 months                  |
| Metrics by month       | 2 years                   |
| Metrics by year        | 5 years                   |
| Service health history | 1 week                    |
| Metadata               | Forever, last record only |
| Ident list             | Forever                   |

## Resetting the database

If for any reason you want to reset the database and remove all data within, you can do so by following this procedure:

1. Stop `gullveig-web` process.
2. Stop `gullveig-server` process.
3. Delete the database file.
4. Start the `gullveig-server` process, wait for it to enter "running" state.
5. Start the `gullveig-web` process.
