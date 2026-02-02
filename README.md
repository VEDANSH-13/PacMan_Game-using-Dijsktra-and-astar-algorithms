🟡 Pac-Man: An Experimental AI Pathfinding Playground

Dijkstra & A* in a Real-Time Game Environment

📖 Project Vision

This project is not just a Pac-Man clone — it is an experimental sandbox for studying and visualizing pathfinding algorithms in real-time.

Built using Python and Pygame, the game transforms the classic Pac-Man maze into a graph-based environment where autonomous agents (Pac-Man and Ghosts) make decisions using Dijkstra’s Algorithm and A* search.

The focus of this project is algorithmic behavior, decision-making, and performance comparison, all wrapped inside an interactive game simulation.

🧠 What Makes This Project Different?

✔️ Algorithm-first design — the maze is treated as a graph, not just tiles
✔️ Autonomous agents — both Pac-Man and ghosts can operate without player input
✔️ Live path visualization — see how algorithms think, not just where they move
✔️ Debug & analysis modes — built for learning, testing, and experimentation
✔️ Separation of logic & rendering — clean architecture for scalability

This makes the project suitable for:

AI & Algorithms coursework

Pathfinding demonstrations

Game AI experimentation

Resume & portfolio showcasing

🎮 Core Features

🤖 Intelligent Ghost AI

Switchable between Dijkstra and A* at runtime

Recalculates paths dynamically as the player moves

🧭 Pac-Man Auto-Navigation

Pac-Man can compute optimal paths to pellets autonomously

Demonstrates shortest-path planning in real environments

🧪 Debug & Visualization Mode

Displays explored nodes, open/closed sets, and final paths

Ideal for understanding algorithm behavior step-by-step

🧱 Graph-Driven Maze

Nodes, edges, and walls form a true weighted graph

Easily extensible for new maps or algorithms

⚙️ Algorithms Implemented
🔹 Dijkstra’s Algorithm

Guarantees the shortest path

Explores uniformly without heuristics

Serves as a baseline for performance comparison

🔹 A* (A-Star) Algorithm

Uses heuristic guidance (Manhattan distance)

Significantly faster in most scenarios

Optimized for real-time decision making

The project allows direct comparison between the two algorithms under identical game conditions.

🛠️ Technology Stack

Python 3.x — Core logic and AI implementation

Pygame — Rendering, input handling, and game loop

Custom Graph System — Built from scratch for full control

Priority Queues & Heuristics — For efficient pathfinding
