import pygame
import sys
import heapq
from dijkstra import dijkstra_next_direction
from astar import astar_next_direction

# Constants
TILE_SIZE = 32
ROWS, COLS = 17, 18
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE  # 576, 544
FPS = 60
GHOST_HOUSE_X, GHOST_HOUSE_Y = 7, 8  # Pick a central, safe tile

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 222)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (222, 33, 33)
PINK = (255, 184, 255)
ORANGE = (255, 184, 82)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

# Maze layout (1 = wall, 0 = dot, 2 = empty, 3 = power pellet, 4 = fruit, 5 = dynamic obstacle)
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,0,0,1,0,0,0,0,1,0,0,3,0,0,0,3,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1],
    [1,0,1,0,0,4,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,0,0,1,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,0,1,0,1,1,0,1,0,1,1,1,0,1,1,1],
    [2,2,1,0,0,0,0,0,0,0,0,1,0,4,0,1,2,2],
    [1,1,1,0,1,1,1,1,1,1,0,1,1,1,0,1,1,1],
    [1,0,4,0,1,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,3,0,0,0,0,1,1,0,0,0,0,3,0,0,0,3,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,4,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,0,0,1,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

class Entity:
    def __init__(self, x, y, color, is_pacman=False, move_delay=1):
        self.x = x
        self.y = y
        self.start_x = x  # For respawning
        self.start_y = y
        self.color = color
        self.dir = (0, 0)
        self.is_pacman = is_pacman
        self.move_delay = move_delay
        self.move_counter = 0
        self.frightened = False
        self.frightened_timer = 0
        self.respawn_timer = 0
        self.next_dir = (0, 0)
        if is_pacman:
            self.mouth_angle = 0.25  # radians, initial mouth open
            self.mouth_direction = 1  # 1 = opening, -1 = closing

    def move(self, maze):
        nx, ny = self.x + self.dir[0], self.y + self.dir[1]
        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
            self.x, self.y = nx, ny

    def animate_mouth(self):
        # Animate mouth between 0.05 and 0.25 radians
        if self.is_pacman:
            self.mouth_angle += 0.02 * self.mouth_direction
            if self.mouth_angle > 0.25:
                self.mouth_angle = 0.25
                self.mouth_direction = -1
            elif self.mouth_angle < 0.05:
                self.mouth_angle = 0.05
                self.mouth_direction = 1

    def draw(self, screen):
        cx = self.x * TILE_SIZE + TILE_SIZE // 2
        cy = self.y * TILE_SIZE + TILE_SIZE // 2
        r = TILE_SIZE // 2 - 2
        if self.is_pacman:
            # Determine mouth direction based on movement
            angle_map = {
                (1, 0): 0,      # right
                (0, -1): 90,    # up
                (-1, 0): 180,   # left
                (0, 1): 270     # down
            }
            angle = angle_map.get(self.dir, 0)
            start_angle = (angle - self.mouth_angle * 180 / 3.14) % 360
            end_angle = (angle + self.mouth_angle * 180 / 3.14) % 360
            # Draw Pac-Man as an arc (mouth open)
            pygame.draw.circle(screen, YELLOW, (cx, cy), r)
            mouth_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.arc(
                screen, BLACK, mouth_rect,
                (angle - self.mouth_angle) * 3.14 / 180,
                (angle + self.mouth_angle) * 3.14 / 180,
                r
            )
            # Draw a filled triangle for the mouth
            mouth_length = r
            mouth_angle_rad = self.mouth_angle * 3.14
            x1 = cx
            y1 = cy
            x2 = cx + mouth_length * pygame.math.Vector2(1, 0).rotate(-angle + self.mouth_angle * 180 / 3.14).x
            y2 = cy + mouth_length * pygame.math.Vector2(1, 0).rotate(-angle + self.mouth_angle * 180 / 3.14).y
            x3 = cx + mouth_length * pygame.math.Vector2(1, 0).rotate(-angle - self.mouth_angle * 180 / 3.14).x
            y3 = cy + mouth_length * pygame.math.Vector2(1, 0).rotate(-angle - self.mouth_angle * 180 / 3.14).y
            pygame.draw.polygon(screen, BLACK, [(x1, y1), (x2, y2), (x3, y3)])
        else:
            if self.respawn_timer > 0:
                return  # Don't draw the ghost while respawning
            color = CYAN if self.frightened else self.color
            pygame.draw.circle(screen, color, (cx, cy), r)

    def move_with_delay(self, maze):
        self.move_counter += 1
        if self.move_counter >= self.move_delay:
            self.move(maze)
            self.move_counter = 0

def draw_maze(screen, maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            if tile == 1:
                pygame.draw.rect(screen, BLUE, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), border_radius=8)
            elif tile == 0:
                pygame.draw.circle(screen, WHITE, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), 4)
            elif tile == 3:
                pygame.draw.circle(screen, WHITE, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), 8)
            elif tile == 4:
                pygame.draw.circle(screen, RED, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2), 7)
                pygame.draw.circle(screen, GREEN, (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2-6), 3)

def is_walkable(x, y, maze):
    return 0 <= x < COLS and 0 <= y < ROWS and maze[y][x] != 1

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    pacman = Entity(7, 10, YELLOW, is_pacman=True, move_delay=6)
    ghosts = [
        Entity(6, 5, RED, move_delay=8),
        Entity(7, 5, PINK, move_delay=8),
        Entity(8, 5, CYAN, move_delay=8),
        Entity(7, 6, ORANGE, move_delay=8)
    ]
    score = 0
    algorithm = "dijkstra"
    lives = 3

    running = True
    paused = False
    debug_mode = False  # Debug mode flag
    auto_pilot = False  # Auto-Pilot mode
    auto_pilot_path = []  # Current path Pac-Man should follow
    auto_pilot_target = None  # (x, y) of current pellet target

    while running:
        lost_life = False
        screen.fill(BLACK)
        draw_maze(screen, MAZE)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if paused:
                    continue
                if event.key == pygame.K_a:
                    auto_pilot = not auto_pilot
                    auto_pilot_path = []
                    auto_pilot_target = None
                if event.key == pygame.K_LEFT:
                    pacman.next_dir = (-1, 0)
                    auto_pilot = False
                elif event.key == pygame.K_RIGHT:
                    pacman.next_dir = (1, 0)
                    auto_pilot = False
                elif event.key == pygame.K_UP:
                    pacman.next_dir = (0, -1)
                    auto_pilot = False
                elif event.key == pygame.K_DOWN:
                    pacman.next_dir = (0, 1)
                    auto_pilot = False
                elif event.key == pygame.K_TAB:
                    algorithm = "astar" if algorithm == "dijkstra" else "dijkstra"
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode

        if paused:
            # Draw "PAUSED" message
            font = pygame.font.SysFont("Arial", 48)
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - 100, HEIGHT // 2 - 24))
            pygame.display.flip()
            clock.tick(10)
            continue

        # --- Auto-Pilot Logic ---
        def find_nearest_pellet(start_x, start_y, maze):
            from collections import deque
            visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
            queue = deque()
            queue.append((start_x, start_y, 0))
            visited[start_y][start_x] = True
            while queue:
                x, y, dist = queue.popleft()
                if maze[y][x] == 0 or maze[y][x] == 3:
                    return (x, y)
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and not visited[ny][nx] and maze[ny][nx] != 1:
                        visited[ny][nx] = True
                        queue.append((nx, ny, dist+1))
            return None

        def get_path(start, goal, maze, algorithm):
            # Returns a list of (x, y) positions from start to goal (including both)
            import heapq
            directions = [(1,0), (-1,0), (0,1), (0,-1)]
            ROWS, COLS = len(maze), len(maze[0])
            dist = [[float('inf') for _ in range(COLS)] for _ in range(ROWS)]
            prev = [[None for _ in range(COLS)] for _ in range(ROWS)]
            if algorithm == "dijkstra":
                heap = []
                heapq.heappush(heap, (0, start[0], start[1]))
                dist[start[1]][start[0]] = 0
                while heap:
                    cost, x, y = heapq.heappop(heap)
                    if (x, y) == goal:
                        break
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
                            new_cost = cost + 1
                            if new_cost < dist[ny][nx]:
                                dist[ny][nx] = new_cost
                                prev[ny][nx] = (x, y)
                                heapq.heappush(heap, (new_cost, nx, ny))
            else:  # astar
                def heuristic(x, y):
                    return abs(x - goal[0]) + abs(y - goal[1])
                heap = []
                heapq.heappush(heap, (heuristic(start[0], start[1]), 0, start[0], start[1]))
                dist[start[1]][start[0]] = 0
                while heap:
                    f, cost, x, y = heapq.heappop(heap)
                    if (x, y) == goal:
                        break
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
                            new_cost = cost + 1
                            if new_cost < dist[ny][nx]:
                                dist[ny][nx] = new_cost
                                prev[ny][nx] = (x, y)
                                heapq.heappush(heap, (new_cost + heuristic(nx, ny), new_cost, nx, ny))
            # Reconstruct path
            path = []
            x, y = goal
            while prev[y][x] is not None and (x, y) != start:
                path.append((x, y))
                x, y = prev[y][x]
            if (x, y) == start:
                path.append((x, y))
                path.reverse()
                return path
            return []

        # --- Pac-Man Movement ---
        if auto_pilot:
            # If no path or target invalid, recalculate
            if not auto_pilot_path or auto_pilot_target is None or MAZE[auto_pilot_target[1]][auto_pilot_target[0]] not in [0,3]:
                target = find_nearest_pellet(pacman.x, pacman.y, MAZE)
                if target:
                    auto_pilot_target = target
                    path = get_path((pacman.x, pacman.y), auto_pilot_target, MAZE, algorithm)
                    auto_pilot_path = path[1:] if len(path) > 1 else []  # skip current pos
                else:
                    auto_pilot_path = []
                    auto_pilot_target = None
            # Move along path if there is one
            if auto_pilot_path:
                next_pos = auto_pilot_path[0]
                dx, dy = next_pos[0] - pacman.x, next_pos[1] - pacman.y
                pacman.next_dir = (dx, dy)
                nx, ny = pacman.x + dx, pacman.y + dy
                if is_walkable(nx, ny, MAZE):
                    pacman.dir = pacman.next_dir
                pacman.move_with_delay(MAZE)
                pacman.animate_mouth()
                # If reached next step, pop it
                if (pacman.x, pacman.y) == next_pos:
                    auto_pilot_path.pop(0)
            else:
                pacman.animate_mouth()
        else:
            nx, ny = pacman.x + pacman.next_dir[0], pacman.y + pacman.next_dir[1]
            if is_walkable(nx, ny, MAZE):
                pacman.dir = pacman.next_dir
            pacman.move_with_delay(MAZE)
            pacman.animate_mouth()
        # Eat dots and power pellets
        if MAZE[pacman.y][pacman.x] == 0:
            MAZE[pacman.y][pacman.x] = 2
            score += 10
        elif MAZE[pacman.y][pacman.x] == 3:
            MAZE[pacman.y][pacman.x] = 2
            score += 50
            for ghost in ghosts:
                ghost.frightened = True
                ghost.frightened_timer = FPS * 7  # 7 seconds
        elif MAZE[pacman.y][pacman.x] == 4:
            MAZE[pacman.y][pacman.x] = 2
            score += 100

        # Move ghosts (using selected algorithm)
        for ghost in ghosts:
            if ghost.respawn_timer > 0:
                ghost.respawn_timer -= 1
                continue  # Skip movement and collision for this ghost

            if ghost.frightened:
                ghost.frightened_timer -= 1
                if ghost.frightened_timer <= 0:
                    ghost.frightened = False
            else:
                if algorithm == "dijkstra":
                    ghost.dir = dijkstra_next_direction(ghost, pacman, MAZE)
                else:
                    ghost.dir = astar_next_direction(ghost, pacman, MAZE)
            ghost.move_with_delay(MAZE)
            # Check collision
            if ghost.x == pacman.x and ghost.y == pacman.y:
                if ghost.frightened:
                    score += 200
                    ghost.x, ghost.y = GHOST_HOUSE_X, GHOST_HOUSE_Y
                    ghost.frightened = False
                    ghost.frightened_timer = 0
                    ghost.respawn_timer = FPS * 2
                    continue
                else:
                    lives -= 1
                    if lives == 0:
                        running = False
                        break
                    else:
                        # Reset positions
                        pacman.x, pacman.y = 7, 10
                        pacman.dir = (0, 0)
                        for g in ghosts:
                            g.x, g.y = g.start_x, g.start_y
                            g.dir = (0, 0)
                        lost_life = True
                        break
            if lost_life:
                break

        # Draw entities
        pacman.draw(screen)
        for ghost in ghosts:
            ghost.draw(screen)

        # Draw ghost paths in debug mode
        if debug_mode:
            path_colors = [RED, PINK, CYAN, ORANGE]
            for idx, ghost in enumerate(ghosts):
                path = get_full_path(ghost, pacman, MAZE, algorithm)
                if path:
                    draw_path(screen, path, path_colors[idx % len(path_colors)])

        # Draw score
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 30))

        # Draw current algorithm
        algo_text = font.render(f"Algorithm: {algorithm.title()}", True, WHITE)
        screen.blit(algo_text, (200, HEIGHT - 30))

        # Draw Auto-Pilot status
        if auto_pilot:
            auto_text = font.render("Auto-Pilot ON (A)", True, CYAN)
            screen.blit(auto_text, (400, HEIGHT - 30))

        # Draw remaining lives as Pac-Man icons
        for i in range(lives):
            pygame.draw.circle(screen, YELLOW, (120 + i * 30, HEIGHT - 15), 10)

        pygame.display.flip()
        clock.tick(FPS)

        if lost_life:
            pygame.time.wait(500)  # Optional: short pause for feedback
            continue  # Skip the rest of the frame

    # Check if player won (no more dots or power pellets left)
    won = True
    for row in MAZE:
        if 0 in row or 3 in row:
            won = False
            break

    if won:
        font = pygame.font.SysFont("Arial", 48)
        win_text = font.render("YOU WIN!", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - 120, HEIGHT // 2 - 24))
        pygame.display.flip()
        pygame.time.wait(2000)
    elif lives == 0:
        font = pygame.font.SysFont("Arial", 48)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 24))
        pygame.display.flip()
        pygame.time.wait(2000)

    pygame.quit()
    sys.exit()

# --- Debug Path Drawing Helpers ---

def get_full_path(ghost, pacman, maze, algorithm):
    # Returns a list of (x, y) positions from ghost to Pac-Man, including both endpoints
    import heapq
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    ROWS, COLS = len(maze), len(maze[0])
    dist = [[float('inf') for _ in range(COLS)] for _ in range(ROWS)]
    prev = [[None for _ in range(COLS)] for _ in range(ROWS)]
    if algorithm == "dijkstra":
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
    else:  # astar
        def heuristic(x, y):
            return abs(x - pacman.x) + abs(y - pacman.y)
        heap = []
        heapq.heappush(heap, (heuristic(ghost.x, ghost.y), 0, ghost.x, ghost.y))
        dist[ghost.y][ghost.x] = 0
        while heap:
            f, cost, x, y = heapq.heappop(heap)
            if (x, y) == (pacman.x, pacman.y):
                break
            for d in directions:
                nx, ny = x + d[0], y + d[1]
                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
                    new_cost = cost + 1
                    if new_cost < dist[ny][nx]:
                        dist[ny][nx] = new_cost
                        prev[ny][nx] = (x, y)
                        heapq.heappush(heap, (new_cost + heuristic(nx, ny), new_cost, nx, ny))
    # Reconstruct path
    path = []
    x, y = pacman.x, pacman.y
    while prev[y][x] is not None and (x, y) != (ghost.x, ghost.y):
        path.append((x, y))
        x, y = prev[y][x]
    if (x, y) == (ghost.x, ghost.y):
        path.append((x, y))
        path.reverse()
        return path
    return None

def draw_path(screen, path, color):
    # Draws a colored line following the path (list of (x, y) tuples)
    if len(path) < 2:
        return
    points = [(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2) for (x, y) in path]
    pygame.draw.lines(screen, color, False, points, 4)

if __name__ == "__main__":
    main()
