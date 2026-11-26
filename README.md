# IPL Fantasy Cricket League

## 1. Project Overview

The IPL Fantasy Cricket League is a backend application developed using Python and FastAPI. It allows users to create fantasy cricket teams, join match contests and earn points from real-world-style player performances.

The application includes role-based access for admins, organizers and users. Organizers manage players, tournaments and matches; users create teams and join contests; and the backend calculates fantasy points and contest rankings automatically.

**Project Type:** Backend Application  
**Technology:** Python, FastAPI, Pydantic, SQLAlchemy, SQLite, JWT  
**Deployment:** Docker and AWS EC2  
**CI/CD:** GitHub Actions and Docker Hub

## 2. Project Team

| Role | Member | Responsibility |
|---|---|---|
| Backend Developer | Lakshya | Tables and Authentication, API 2(login),Implimented 5 endpoints and repository/deployment setup |
| Backend Developer | Thammiksha |API 3(Refersh), Implimented 5 endpoints,repository/deployment setup |
| Backend Developer | Thanmayee |  API 1 (Register), Implimented 5 endpoints,repository/deployment setup |


### 3-Day Work Plan

| Member | Day 1 | Day 2 | Day 3 |
|---|---|---|---|
| Lakshya | Implimented Tables and repository/deployment setup | Implimented Authentication and Implimented API's and Endpoints 1,4 | Implimented remaining endpoints and updated README.md. |
| Thammiksha | Implimented Tables and repository/deployment setup | Implimented API's and Implimented Endpoints 2,5 | Implimented reaming endpoints and README.md |
| Thanmayee | Implimented Tables and repository/deployment setup|  Implimented API's and Implimented Endpoints 3,6 |Implimented reaming endpoints and README.md |

## 3. Live App

| Item | URL |
|---|---|
| API |  http://0.0.0.0:8000  |
| Swagger Documentation | http://32.199.180.3:8000/docs |
| Docker Hub Image | lakhya1196/ipl-fantasy:v1.0.1 |

## 4. How to Run It
### Run Locally

```bash
git clone [GITHUB_REPOSITORY_URL]
cd ipl-fantasy-cricket-league/backend

python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open:
<img width="748" height="618" alt="image" src="https://github.com/user-attachments/assets/8b8d925a-0d4b-480d-9304-9373e9c881d9" />


## 5. API Contract

### Authentication APIs

| ID | Functionality | Method | Endpoint |
|---|---|---|---|
| A1 | Register a new account | POST | `/auth/register` |
| A2 | Login and generate access and refresh tokens | POST | `/auth/login` |
| A3 | Generate a new access token | POST | `/auth/refresh` |

### Project-Specific APIs

| ID | Functionality | Access | Method | Endpoint |
|---|---|---|---|---|
| E1 | Create an organizer account | Admin | POST | `/admin/organizers` |
| E2 | Add a cricket player | Organizer | POST | `/organizer/players` |
| E3 | Get all available cricket players | All | GET | `/players` |
| E4 | Get details of a player | All | GET | `/players/{player_id}` |
| E5 | Create a cricket tournament | Organizer | POST | `/organizer/tournaments` |
| E6 | Get all tournaments | All | GET | `/tournaments` |
| E7 | Create a fantasy team | User | POST | `/fantasy-teams` |
| E8 | Add a player to a fantasy team | User | POST | `/fantasy-teams/{team_id}/players/{player_id}` |
| E9 | Remove a player from a fantasy team | User | DELETE | `/fantasy-teams/{team_id}/players/{player_id}` |
| E10 | Get the logged-in user's fantasy teams | User | GET | `/users/me/fantasy-teams` |
| E11 | Create a fantasy contest for a match | Organizer | POST | `/organizer/contests` |
| E12 | Join a contest using a fantasy team | User | POST | `/contests/{contest_id}/join` |
| E13 | Publish player performance statistics | Organizer | POST | `/organizer/matches/{match_id}/performances` |
| E14 | Get a contest leaderboard | All | GET | `/contests/{contest_id}/leaderboard` |
| E15 | Get a user's fantasy points history | User | GET | `/users/me/fantasy-points` |

Example request bodies:

```json
// POST /auth/register
{
  "name": "User Name",
  "email": "user@example.com",
  "password": "secure-password"
}
```

```json
// POST /organizer/players
{
  "name": "Virat Kohli",
  "role": "batsman",
  "team": "RCB",
  "base_points": 100
}
```

```json
// POST /fantasy-teams
{
  "name": "My Dream XI"
}
```

```json
// POST /organizer/matches/{match_id}/performances
{
  "player_id": 1,
  "runs": 50,
  "fours": 5,
  "sixes": 2,
  "wickets": 1,
  "catches": 2,
  "run_outs": 0,
  "stumpings": 0
}
```

## 6. Business Rules

- New registrations receive the `user` role.
- Only an admin can create organizer accounts.
- A player requires a name, role, team and base points.
- Player roles are `batsman`, `bowler`, `all-rounder` and `wicketkeeper`.
- A fantasy team has a name and cannot contain more than 11 players.
- Fantasy teams must follow configured role limits.
- Players can be added or removed until the match deadline.
- A contest must be associated with a match.
- A fantasy team can join a contest only once.
- Fantasy points are calculated automatically after organizer-published performances.
- The contest leaderboard ranks users by total fantasy points.

### Fantasy Scoring

| Performance | Points |
|---|---:|
| Run scored | 1 |
| Four hit | 1 bonus |
| Six hit | 2 bonus |
| Wicket taken | 25 |
| Catch | 8 |
| Run out | 12 |
| Stumping | 12 |

## 7. Database Design

- `users`
- `roles`
- `players`
- `tournaments`
- `matches`
- `fantasy_teams`
- `fantasy_team_players`
- `contests`
- `contest_entries`
- `player_performance`
- `fantasy_points`

## 8. Docker and AWS Deployment

- Build the FastAPI application as a Docker image.
- Run the container on port `8000`.
- Use an AWS EC2 instance with a public IP.
- Configure the EC2 security group to allow SSH and TCP port `8000`.
- Access the public API at `http://32.199.180.3:8000/docs`.

## 9. CI/CD Deployment

GitHub Actions build the Docker image, push it to Docker Hub and deploy it to EC2.

Configure the GitHub Actions secrets.

Deployment pulls the latest image, stop and remove the existing container, and start a replacement with the SQLite directory mounted persistently.
<img width="928" height="814" alt="Screenshot 2026-11-26 120347" src="https://github.com/user-attachments/assets/cb7f1eab-3b2e-4311-9460-2c2c591b12c8" />

