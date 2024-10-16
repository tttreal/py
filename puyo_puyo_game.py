import pygame
import random

# 定数
GRID_WIDTH = 6
GRID_HEIGHT = 12
CELL_SIZE = 40
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]  # 赤、青、緑、黄

# Pygameの初期化
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Puyo:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

class Game:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_pair = self.new_pair()
        self.next_pair = self.new_pair()
        self.fall_time = 0
        self.fall_speed = 0.5  # 0.5秒ごとに落下
        self.score = 0
        self.fast_fall = False  # 高速落下フラグ

    def new_pair(self):
        return [Puyo(GRID_WIDTH // 2 - 1, 0, random.choice(COLORS)),
                Puyo(GRID_WIDTH // 2, 0, random.choice(COLORS))]

    def check_collision(self, pair):
        # ぷよペアが既存のぷよと衝突するかチェック
        for puyo in pair:
            if self.grid[puyo.y][puyo.x] is not None:
                return True
        return False

    def move(self, dx):
        for puyo in self.current_pair:
            new_x = puyo.x + dx
            if 0 <= new_x < GRID_WIDTH and self.grid[puyo.y][new_x] is None:
                puyo.x = new_x
            else:
                return

    def rotate(self):
        p1, p2 = self.current_pair
        if p1.y == p2.y:  # 横並びの場合
            if p1.x < p2.x:  # p1が左
                if p1.y > 0 and self.grid[p1.y - 1][p1.x] is None:
                    p2.x, p2.y = p1.x, p1.y - 1
            else:  # p2が左
                if p2.y > 0 and self.grid[p2.y - 1][p2.x] is None:
                    p1.x, p1.y = p2.x, p2.y - 1
        else:  # 縦並びの場合
            if p1.y < p2.y:  # p1が上
                if p1.x < GRID_WIDTH - 1 and self.grid[p1.y][p1.x + 1] is None:
                    p2.x, p2.y = p1.x + 1, p1.y
                elif p1.x > 0 and self.grid[p1.y][p1.x - 1] is None:
                    p2.x, p2.y = p1.x - 1, p1.y
            else:  # p2が上
                if p2.x < GRID_WIDTH - 1 and self.grid[p2.y][p2.x + 1] is None:
                    p1.x, p1.y = p2.x + 1, p2.y
                elif p2.x > 0 and self.grid[p2.y][p2.x - 1] is None:
                    p1.x, p1.y = p2.x - 1, p2.y

    def update(self, dt):
        self.fall_time += dt
        fall_interval = 0.05 if self.fast_fall else self.fall_speed
        if self.fall_time >= fall_interval:
            self.fall_time = 0
            self.move_down()

    def move_down(self):
        can_move = True
        for puyo in self.current_pair:
            if puyo.y + 1 >= GRID_HEIGHT or self.grid[puyo.y + 1][puyo.x] is not None:
                can_move = False
                break
        
        if can_move:
            for puyo in self.current_pair:
                puyo.y += 1
        else:
            self.place_puyos()
            self.check_connections()
            self.current_pair = self.next_pair
            self.next_pair = self.new_pair()
            self.fast_fall = False

    def place_puyos(self):
        for puyo in self.current_pair:
            self.grid[puyo.y][puyo.x] = puyo

    def check_connections(self):
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        to_remove = []

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] and not visited[y][x]:
                    connected = self.dfs(x, y, self.grid[y][x].color, visited)
                    if len(connected) >= 4:
                        to_remove.extend(connected)

        if to_remove:
            self.remove_puyos(to_remove)
            self.apply_gravity()
            self.score += len(to_remove) * 10
            self.check_connections()  # 連鎖のチェック

    def dfs(self, x, y, color, visited):
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT or visited[y][x] or not self.grid[y][x] or self.grid[y][x].color != color:
            return []
        
        visited[y][x] = True
        connected = [(x, y)]
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            connected.extend(self.dfs(x + dx, y + dy, color, visited))
        return connected

    def remove_puyos(self, to_remove):
        for x, y in to_remove:
            self.grid[y][x] = None

    def apply_gravity(self):
        for x in range(GRID_WIDTH):
            column = [self.grid[y][x] for y in range(GRID_HEIGHT) if self.grid[y][x]]
            for y in range(GRID_HEIGHT - 1, -1, -1):
                if column:
                    puyo = column.pop()
                    puyo.y = y
                    self.grid[y][x] = puyo
                else:
                    self.grid[y][x] = None

    def draw(self, screen):
        # グリッド上のぷよを描画
        for y, row in enumerate(self.grid):
            for x, puyo in enumerate(row):
                if puyo:
                    pygame.draw.circle(screen, puyo.color,
                                       (x * CELL_SIZE + CELL_SIZE // 2,
                                        y * CELL_SIZE + CELL_SIZE // 2),
                                       CELL_SIZE // 2 - 2)

        # 現在落下中のぷよペアを描画
        for puyo in self.current_pair:
            pygame.draw.circle(screen, puyo.color,
                               (puyo.x * CELL_SIZE + CELL_SIZE // 2,
                                puyo.y * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 2 - 2)

        # 次のぷよペアとスコアの表示
        for i, puyo in enumerate(self.next_pair):
            pygame.draw.circle(screen, puyo.color,
                               ((GRID_WIDTH + 1) * CELL_SIZE // 2,
                                (i + 1) * CELL_SIZE),
                               CELL_SIZE // 2 - 2)

        # スコア表示
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

game = Game()

running = True
while running:
    dt = clock.tick(60) / 1000.0  # デルタ時間を秒単位で取得

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game.move(-1)
            elif event.key == pygame.K_RIGHT:
                game.move(1)
            elif event.key == pygame.K_DOWN:
                game.fast_fall = True
            elif event.key == pygame.K_UP:
                game.rotate()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                game.fast_fall = False

    game.update(dt)

    screen.fill((0, 0, 0))
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
