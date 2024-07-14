Write class `DataManager` which is dedicated to downloading and keeping stock data up to date.
It will use the 1min data from Polygon.io. It will use that 1min data to derive the 5min, 15min, 30min, 1h, 1d, 5d & weekly data.
It will have a method `setup` to do the initial download of 5 years of 1min data, and another method `tick` that will be called regularly from a cron job, to download only the missing data.
It will have a `postProcess` function that will calculate extra columns.
It will have methods `resetData()` & `saveData()` to clear the data from the database & add data to the database.

- onSetup:
    - For each symbol:
        - Download 5y of 1min data
        - Calculate the 5min, 15min, 30min, 1h, 1d, 5d out of the 1min, making sure to respect proper start & end time for each, to match stock market timeframes.
        - Run `postProcess(data)` for every timeframe to calculate the extra data columns
        - Erase the existing data via `resetData()`
        - Save the data via `saveData(data)`

- onTick:
    - For each symbol:
        - Fetch the last available 1min data
        - Download the 1min data to fill the data hole since the last data available
        - Do the same for the 5min, 15min, 30min, 1h, 1d, 5d timeframes, using the 1min data.
        - Run `postProcess(data[-250])` (last 250 datapoints minimum, or more if the data hole was larger) for every timeframe to recalculate the extra data columns
        - Save the data via `saveData()`, adding the new datapoints and updating the existing ones



