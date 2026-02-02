import heapq

def dijkstra_next_direction(ghost, pacman, maze):
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    ROWS, COLS = len(maze), len(maze[0])
    dist = [[float('inf') for _ in range(COLS)] for _ in range(ROWS)]
    prev = [[None for _ in range(COLS)] for _ in range(ROWS)]
    heap = []
    heapq.heappush(heap, (0, ghost.x, ghost.y))
    dist[ghost.y][ghost.x] = 0

    while heap:
        cost, x, y = heapq.heappop(heap)
        if (x, y) == (pacman.x, pacman.y):
            break
        for d in directions:
            nx, ny = x + d[0], y + d[1]
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
                new_cost = cost + 1
                if new_cost < dist[ny][nx]:
                    dist[ny][nx] = new_cost
                    prev[ny][nx] = (x, y)
                    heapq.heappush(heap, (new_cost, nx, ny))

    # Reconstruct path
    path = []
    x, y = pacman.x, pacman.y
    while prev[y][x] is not None and (x, y) != (ghost.x, ghost.y):
        px, py = prev[y][x]
        path.append((x - px, y - py))
        x, y = px, py
    if path:
        return path[-1]  # First step from ghost to Pac-Man
    else:
        return ghost.dir  # No path found or already at Pac-Man
