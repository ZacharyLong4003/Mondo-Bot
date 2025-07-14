# Mondo Bot

Mondo Bot is a Discord bot inspired by Discord's Trick-or-Treat bot. It runs timed challenge events where users race to respond correctly for points. Scores are tracked persistently, and the top user earns a special server role.

## Features

- Timed "Back" or "Over" challenges
- Decreasing point value over time
- Double points if someone answers incorrectly first
- Persistent leaderboard (saved to `leaderboard.txt`)
- Automatic monthly champion role assignment
- Simple command interface

## Commands

- `m!leaderboard` – View the leaderboard  
- `m!chal` – Start a challenge manually  
- `m!end` – End an active challenge  
- `m!back` – Respond "Back" to a challenge  
- `m!over` – Respond "Over" to a challenge  
- `m!champ` – Force update the champion role  
- `m!mondo_help` – List available commands  

## Setup

1. Install `discord.py`  
   ```bash
   pip install -U discord.py
