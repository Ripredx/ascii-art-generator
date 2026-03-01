from typing import List, Tuple, Optional

Matrix = List[List[str]]
Coordinate = Tuple[int, int]


class DrawEngine:
    def __init__(self, width: int = 80, height: int = 30):
        self.width = width
        self.height = height
        self.matrix: Matrix = [
            [" " for _ in range(self.width)] for _ in range(self.height)
        ]
        self.preview_matrix: Optional[Matrix] = None
        self.shape_start_pos: Optional[Coordinate] = None

    def clear(self):
        self.matrix = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.preview_matrix = None
        self.shape_start_pos = None

    def render_to_string(self) -> str:
        matrix_to_render: Matrix = (
            self.preview_matrix if self.preview_matrix is not None else self.matrix
        )
        return "\n".join("".join(row) for row in matrix_to_render)

    def paint(self, r: int, c: int, char: str):
        if 0 <= r < self.height and 0 <= c < self.width:
            self.matrix[r][c] = char

    def flood_fill(self, r: int, c: int, target_char: str):
        if not (0 <= r < self.height and 0 <= c < self.width):
            return
        target_color = self.matrix[r][c]
        if target_color == target_char:
            return

        queue: List[Coordinate] = [(r, c)]
        self.matrix[r][c] = target_char

        while queue:
            curr_r, curr_c = queue.pop(0)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if self.matrix[nr][nc] == target_color:
                        self.matrix[nr][nc] = target_char
                        queue.append((nr, nc))

    def begin_shape(self, r: int, c: int):
        self.shape_start_pos = (r, c)

    def end_shape(self):
        if self.preview_matrix is not None:
            self.matrix = self.preview_matrix
        self.preview_matrix = None
        self.shape_start_pos = None

    def preview_line(self, r1: int, c1: int, char: str):
        if not self.shape_start_pos:
            return
        r0, c0 = self.shape_start_pos
        self.preview_matrix = [row[:] for row in self.matrix]
        self._draw_line(self.preview_matrix, r0, c0, r1, c1, char)

    def preview_rect(self, r1: int, c1: int, char: str):
        if not self.shape_start_pos:
            return
        r0, c0 = self.shape_start_pos
        self.preview_matrix = [row[:] for row in self.matrix]
        self._draw_rect(self.preview_matrix, r0, c0, r1, c1, char)

    def _draw_line(self, m: Matrix, r0: int, c0: int, r1: int, c1: int, char: str):
        dr: int = abs(r1 - r0)
        dc: int = abs(c1 - c0)
        sr: int = 1 if r0 < r1 else -1
        sc: int = 1 if c0 < c1 else -1
        err: int = dc - dr
        while True:
            if 0 <= r0 < self.height and 0 <= c0 < self.width:
                m[r0][c0] = char
            if r0 == r1 and c0 == c1:
                break
            e2: int = 2 * err
            if e2 > -dr:
                err -= dr
                c0 += sc
            if e2 < dc:
                err += dc
                r0 += sr

    def _draw_rect(self, m: Matrix, r0: int, c0: int, r1: int, c1: int, char: str):
        min_r, max_r = min(r0, r1), max(r0, r1)
        min_c, max_c = min(c0, c1), max(c0, c1)
        for r in range(min_r, max_r + 1):
            if 0 <= r < self.height:
                if 0 <= min_c < self.width:
                    m[r][min_c] = char
                if 0 <= max_c < self.width:
                    m[r][max_c] = char
        for c in range(min_c, max_c + 1):
            if 0 <= c < self.width:
                if 0 <= min_r < self.height:
                    m[min_r][c] = char
                if 0 <= max_r < self.height:
                    m[max_r][c] = char
