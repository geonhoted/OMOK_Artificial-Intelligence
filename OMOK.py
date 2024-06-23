

from math import sqrt, log
import random
import time

n = 19
k = 5
start = '-' * (n * n)

class Node():
    def __init__(self, state, player=None, pos=None, parent=None):
        self.state = state
        self.player = player
        self.pos = pos
        self.parent = parent
        self.nwin = 0
        self.nvisit = 0
        self.untried = get_empty(state)
        self.children = []

    def UCTselect(self):
        return sorted(self.children, key=lambda c: c.nwin / c.nvisit + sqrt(log(self.nvisit) / c.nvisit))[-1]

    def makeChild(self, state, pos, player):
        node = Node(state, player, pos, parent=self)
        self.untried.remove(pos)
        self.children.append(node)
        return node

    def update(self, winner):
        self.nvisit += 1
        if winner == 'T':
            self.nwin += 0.5
        elif winner == self.player:
            self.nwin += 1

def get_empty(state):
    empty = []
    if decide_winner(state) in ['B', 'W', 'T']:
        return empty
    for i in range(len(state)):
        if state[i] == '-':
            r, c = i // n, i % n
            for dy, dx in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                ny, nx = r + dy, c + dx
                if 0 <= ny < n and 0 <= nx < n and state[ny * n + nx] == '-' and (ny * n + nx) not in empty:
                    empty.append(ny * n + nx)
    return empty

def decide_winner(state):
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for i in range(n * n):
        if state[i] != '-':
            player = state[i]
            r, c = i // n, i % n
            for dr, dc in directions:
                count = 1
                for d in [1, -1]:
                    nr, nc = r + dr * d, c + dc * d
                    while 0 <= nr < n and 0 <= nc < n and state[nr * n + nc] == player:
                        nr += dr * d
                        nc += dc * d
                        count += 1
                        if count == k:
                            return player
    return 'N' if '-' in state else 'T'

def evaluate_position(state, pos, player):
    score = 0
    opponent = 'W' if player == 'B' else 'B'
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1), (1, -1), (0, -1), (-1, -1), (-1, 0)]
    n = int(sqrt(len(state)))
    r, c = pos // n, pos % n

    # 상대방의 3개나 4개의 연속된 돌이 있는 경우에 대한 방어 수행
    for dr, dc in directions:
        line_length = 1
        open_ends = 0
        opponent_threat = 0

        # 양 방향 탐색
        for direction in [1, -1]:
            for step in range(1, 5):
                nr, nc = r + dr * step * direction, c + dc * step * direction
                if 0 <= nr < n and 0 <= nc < n:
                    if state[nr * n + nc] == player:
                        line_length += 1
                    if line_length >= 3:
                        empty_spaces = [(r + dr * i * direction, c + dc * i * direction) for i in range(1, 5) if 0 <= r + dr * i * direction < n and 0 <= c + dc * i * direction < n and state[(r + dr * i * direction) * n + (c + dc * i * direction)] == '-']
                        if len(empty_spaces) > 0:
                            left_space = empty_spaces[0]
                            right_space = empty_spaces[-1]
                            if random.choice([True, False]):  # 랜덤으로 양쪽 중 하나 선택
                                middle_space = left_space
                            else:
                                middle_space = right_space
                            score += 1000000  # 막는 위치에 가중치 부여

    return score

def mcts(state, player, start_time, time_limit=30):
    root = Node(state, player=player)
    best_move = None
    best_score = float('-inf')

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > time_limit:
            print(f"Time limit exceeded after {elapsed_time} seconds.")
            break

        node = root
        while node.untried == [] and node.children != []:
            node = node.UCTselect()
            state = Move(state, node.pos, player)
            player = switch_player(player)

        if node.untried != []:
            pos = mcts_heuristic(state, player)  # 휴리스틱 함수 사용
            if pos is not None:
                state = Move(state, pos, player)
                node = node.makeChild(state, pos, player)

        winner = decide_winner(state)
        while node:
            node.update(winner)
            if node.nwin / node.nvisit > best_score:
                best_score = node.nwin / node.nvisit
                best_move = node.pos
            node = node.parent

    print(f"Best move found in given time: {best_move} with score {best_score}")
    return best_move





def mcts_heuristic(state, player):
    empty_positions = get_empty(state)
    best_score = -float('inf')
    best_move = None

    for pos in empty_positions:
        if state[pos] == '-':
            potential_state = state[:pos] + [player] + state[pos+1:]
            move_score = evaluate_position(potential_state, pos, player)
            #print(f"Move at {pos} scores {move_score}")  # 로깅 추가
            if move_score > best_score:
                best_score = move_score
                best_move = pos

    return best_move


#def mcts(state, player, start_time, time_limit=30):
    root = Node(state, player=player)
    best_move = None
    best_score = float('-inf')

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > time_limit:
            print(f"Time limit exceeded after {elapsed_time} seconds.")
            break

        node = root
        while node.untried == [] and node.children != []:
            node = node.UCTselect()
            state = Move(state, node.pos, player)
            player = switch_player(player)

        if node.untried != []:
            pos = mcts_heuristic(state, player)  # 휴리스틱 함수 사용
            if pos is not None:
                state = Move(state, pos, player)
                node = node.makeChild(state, pos, player)

        winner = decide_winner(state)
        while node:
            node.update(winner)
            if node.nwin / node.nvisit > best_score:
                best_score = node.nwin / node.nvisit
                best_move = node.pos
            node = node.parent

    print(f"Best move found in given time: {best_move} with score {best_score}")
    return best_move


def Move(state, pos, player):
    return state[:pos] + [player] + state[pos + 1:]


def print_board(state):
    print("  " + " ".join([str(i) for i in range(n)]))
    for i in range(n):
        row_display = f"{i:2}" + " " + " ".join(state[n*i:n*(i+1)].replace('-', '.').replace('B', '●').replace('W', '○'))
        print(row_display)

def get_position_input():
    while True:
        input_str = input("Enter your move (row col): ")
        try:
            row, col = map(int, input_str.split())
            if 0 <= row < n and 0 <= col < n:
                return row * n + col
            else:
                print("Invalid position. Please enter values between 0 and 18.")
        except ValueError:
            print("Invalid input. Please enter two integers separated by space.")

def switch_player(player):
    return 'W' if player == 'B' else 'B'

def omok_play():
    player_choice = input("Choose your color - Black (B) or White (W): ").strip().upper()
    while player_choice not in ['B', 'W']:
        player_choice = input("Invalid choice. Please choose Black (B) or White (W): ").strip().upper()
    
    state = list(start)  # 게임 상태 초기화
    current_player = 'B'
    print_board("".join(state))
    
    while True:
        start_time = time.time()
        if current_player == player_choice:
            while True:
                if time.time() - start_time > 30:
                    print(f"Time's up! {current_player} failed to make a move in time.")
                    break
                pos = get_position_input()
                if state[pos] == '-':
                    state[pos] = current_player
                    break
                else:
                    print("Position already taken. Choose another position.")
        else:
            while time.time() - start_time < 30:
                print(f"{current_player}'s (AI) move...")
                pos = mcts(state, current_player, start_time, 10)  # MCTS를 사용하여 수 계산
                if pos is not None:
                    state[pos] = current_player
                break

        print_board("".join(state))
        winner = decide_winner("".join(state))
        if winner != 'N':
            print('Game over. Tie' if winner == 'T' else f'{winner} wins.')
            break
        if time.time() - start_time > 30:
            print(f"30초 제한 초과: {current_player}의 턴을 넘깁니다.")
            current_player = switch_player(current_player)
            continue

        current_player = switch_player(current_player)

# 게임 시작
omok_play()
