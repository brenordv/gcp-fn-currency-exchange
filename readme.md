# Google Cloud Platform - timer-trigger function.
## The idea of this project
I usually use Microsoft Azure as my preferred cloud environment, but I wanted to check how complex it
would be to create a timer-triggered function in Google Cloud Platform.

The focus here is not what the function does per se, but I needed the function to do something.

Unlike Azure, GCP do not have a timer-trigger function, but this can be achieved easily using a `Pub/Sub function` and a
`Cloud Scheduler` job.

The way it works is: The Pub/Sub function waits for a message to be posted to a specific topic.
Meanwhile, the Cloud Scheduler job will post a message to this topic according to the frequency defined 
(0 */1 * * * for running once every hour). 

The content of the message is irrelevant, since it's used just to trigger the function.

This setup worked perfectly for me and all in the free tier.


## What this function do
It's a smiple application that i through together. At the top of every hour, the function will check the exchange price for CAD to BRL and if 
it's outside a defined threshold, it will message me @ telegram.

## How to run this function locally
First, you need the following variables:
- **alpha_vantage_key**: Key for exchange API. You can get one free at their website - https://www.alphavantage.co
- **mongo_user**: mongo db user. You can get one free from MongoDb Atlas - https://cloud.mongodb.com
- **mongo_pass**: mongo db password. 
- **mongo_database**: mongo db database name
- **telegram_bot_key**: Bot key. You can get one from the BotFather (https://core.telegram.org/bots)
- **telegram_chat_id**: The id of the chat that will receive all notifications.
- **threshold**: Threshold in percentile. Default: 0.05 (5%)
- **from_currency**: "From" currency. Default: CAD
- **to_currency**: "To" currency. Default: BRL

Those can be added as environment variables or as a json in a file called secrets.json (that should be placed in the 
same folder as the scripts).

To execute the function, just run `func.py` file.

## Notes
### 1. Why there's no tests for this function?
Because the focus here is not the function itself, but the setup to run execute a function once every hour.

