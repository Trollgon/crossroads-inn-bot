# The Crossrods Inn - Ready Check Bot
This is a Discord bot that allows trainees to apply for tiers in [The Crossroads Inn](https://discord.gg/hdhDE3v). 
It is written in Python and uses the discord.py library.

The bot uses the Guild Wars 2 API to check if a user has the required achievements, mastery and equipment for a tier.
The equipment is checked by comparing the user's equipment with the suggested equipment from [Snow Crows](https://snowcrows.com/en/home).
In case the user's equipment differs from the suggested equipment, a manual gear check can be requested.

## Setup with `docker compose`
Add the missing environment variables to the `docker-compose.yml` file and run `docker-compose up -d`.

## Environment variables
| Variable | Description                                                                    |
|----------|--------------------------------------------------------------------------------|
| `DISCORD_TOKEN` | The bot token from the Discord developer portal.                               |
| `LOG_CHANNEL_ID` | The ID of the channel where the bot should log.                                |
| `RR_CHANNEL_ID` | The ID of the channel where the manual gear checks are posted.                 |
| `TIER_ASSIGNMENT_CHANNEL_ID` | The ID of the channel where the bot should post the tier assignments messages. |
| `T0_ROLE_ID` | The ID of the role for tier 0.                                                 |
| `T1_ROLE_ID` | The ID of the role for tier 1.                                                 |
| `T2_ROLE_ID` | The ID of the role for tier 2.                                                 |
| `T3_ROLE_ID` | The ID of the role for tier 3.                                                 |
| `DATABASE_URL` | The URL of the database.                                                       |


## Screenshots

#### How to use:
![](https://cdn.discordapp.com/attachments/855781086792253461/1100401026609184828/image.png)

#### Achievements & Mastery Check:
![](https://cdn.discordapp.com/attachments/855781086792253461/1100401948257157140/image.png)

#### Automatic Equipment Review:
![](https://cdn.discordapp.com/attachments/855781086792253461/1100403410278297660/image.png)

#### Manual Equipment Review:
![](https://cdn.discordapp.com/attachments/855781086792253461/1100400503273312337/Screenshot_2023-04-25_143719.png)