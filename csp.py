import itertools
import random

class Sentence():
    """
    Ý nghĩa: Một “câu” mô tả: trong tập các ô cells, 
    có đúng count ô là mìn. Ví dụ: {(1,1),(1,2),(2,1)} = 1
    """

    def __init__(self, cells, count):
        self.cells = set(cells)# tập hợp các ô 
        self.count = count# đến số ô mìn trong tập hợp cells

    def __eq__(self, other):# so sánh xem 2 câu có trùng nhau không nếu đúng trả về True
        return self.cells == other.cells and self.count == other.count

    def __str__(self): # chuyển về chuỗi
        return f"{self.cells} = {self.count}"

    def known_mines(self): # xách định các ô chắc chắn là mìn 
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self): # xác định các ô chắc chắn an toàn 
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell): # cập nhật lại câu nếu ô đó là mìn 
        # xóa ô cell khỏi self.cells và giảm self.count đi 1 
        newCells = set()
        for item in self.cells:
            if item != cell:
                newCells.add(item)
            else:
                self.count -= 1
        self.cells = newCells

    def mark_safe(self, cell): # cập nhật lại câu nếu ô đó là an toàn 
        #xóa ô cell khỏi self.cells và không giảm self.count 
        newCells = set()
        for item in self.cells:
            if item != cell:
                newCells.add(item)
        self.cells = newCells
        


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set() #các ô đã mở 

        # Keep track of cells known to be safe or mines
        self.mines = set() # các ô chắc chắn là mìn
        self.safes = set()#các ô chắc chắn là an toàn

        # List of sentences about the game known to be true
        self.knowledge = []# danh sách các câu đã biết 

    def mark_mine(self, cell):
        """
        Đánh dấu một ô là mìn và cập nhật tất cả câu
        để đánh dấu ô đó cũng là mìn.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Đánh dấu một ô là an toàn và cập nhật tất cả câu
        để đánh dấu ô đó cũng an toàn.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        # Mark cell as safe and add to moves_made
        self.mark_safe(cell)
        self.moves_made.add(cell)

        # Create and Add sentence to knowledge
        neighbors, count = self.get_cell_neighbors(cell, count)
        """
        lấy các ô lân cận chưa biết làm tập neighbors , điều chỉnh count 
        trừ đi số ô lân cận đã biết là mìn(vì các ô mìn 
        đã biết không nên nằm trong câu mới)
        """
        sentence = Sentence(neighbors, count)
        self.knowledge.append(sentence)
        new_inferences = []
        #(3)Suy luận bằng quan hệ tập con/tập lớn
        for s in self.knowledge: 
            if s == sentence:
                continue
            elif s.cells.issuperset(sentence.cells):#Nếu s.cells bao sentence.cells (s là tập lớn, câu mới là tập con):
                setDiff = s.cells-sentence.cells# phần chênh lệch giữa 2 tập hợp
                # Known safes
                if s.count == sentence.count: # -> phần chêcnh lệch không có mìn -> toàn bộ set diff là an toàn 
                    for safeFound in setDiff:
                        self.mark_safe(safeFound)
                # Known mines
                elif len(setDiff) == s.count - sentence.count: # ->phần chênh lệch là mìn -> toàn bộ set diff là mìn 
                    for mineFound in setDiff:
                        self.mark_mine(mineFound)
                # Known inference
                else: # nếu không có 2 cái kia thì suy ra câu mới 
                    new_inferences.append(
                        Sentence(setDiff, s.count - sentence.count)
                    )
            elif sentence.cells.issuperset(s.cells):#sentence.cells bao s.cells
                setDiff = sentence.cells-s.cells
                # Known safes
                if s.count == sentence.count:
                    for safeFound in setDiff:
                        self.mark_safe(safeFound)
                # Known mines
                elif len(setDiff) == sentence.count - s.count:
                    for mineFound in setDiff:
                        self.mark_mine(mineFound)
                # Known inference
                else:
                    new_inferences.append(
                        Sentence(setDiff, sentence.count - s.count)
                    )
        """
        (4) Làm sạch knowledge
        """
        self.knowledge.extend(new_inferences)
        self.remove_dups() # loại bỏ các câu trùng lặp
        self.remove_sures()#để gặt hái kết quả chắc chắn

    def make_safe_move(self):
        """
        trả về một ô an toàn để chọn trên bảng Dò mìn.
        Nước đi phải được xác định là an toàn, và chưa phải là nước đi
        đã được thực hiện.
        Hàm này có thể sử dụng kiến thức trong self.mines, self.safes
        và self.moves_made, nhưng không được sửa đổi bất kỳ giá trị nào trong số đó.
        """
        safeCells = self.safes - self.moves_made
        if not safeCells:
            return None
        # print(f"Pool: {safeCells}")
        move = safeCells.pop()
        return move

    def make_random_move(self):
        """
        Trả về một nước đi cần thực hiện trên bảng Dò mìn.
        Nên chọn ngẫu nhiên trong số các ô:
        1) chưa được chọn, và
        2) không được biết là có mìn
        """
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.mines and (i,j) not in self.moves_made:
                    all_moves.add((i,j))
        # No moves left
        if len(all_moves) == 0:
            return None
        # Return available
        move = random.choice(tuple(all_moves))
        return move
               
    def get_cell_neighbors(self, cell, count):
        #Tìm ra danh sách hàng xóm chưa biết quanh ô đó.
        #Điều chỉnh lại số mìn count nếu trong các hàng xóm đã có ô nào chắc chắn là mìn.
        i, j = cell
        neighbors = []
        # quét hình vuông 3x3 quanh cell 
        for row in range(i-1, i+2):
            for col in range(j-1, j+2):
                if (row >= 0 and row < self.height) \
                and (col >= 0 and col < self.width) \
                and (row, col) != cell \
                and (row, col) not in self.safes \
                and (row, col) not in self.mines:
                #lọc ô trong bàn và chưa nằm trong an toàn hoặc mìn
                    neighbors.append((row, col))
                if (row, col) in self.mines: # nếu ô nằm trong mines thì giảm count đi 1
                    count -= 1

        return neighbors, count

    def remove_dups(self):
        unique_knowledge = []
        for s in self.knowledge:
            if s not in unique_knowledge:
                unique_knowledge.append(s)
        self.knowledge = unique_knowledge

    def remove_sures(self):
        final_knowledge = []
        for s in self.knowledge:
            final_knowledge.append(s)
            if s.known_mines():  # nếu có ô mìn chắc chắn
                for mineFound in s.known_mines():
                    self.mark_mine(mineFound) # thêm vào mìn
                final_knowledge.pop(-1)#loại bỏ câu đó
            elif s.known_safes():# nếu có ô an toàn chắc chắn
                for safeFound in s.known_safes():
                    self.mark_safe(safeFound)# thêm vào ô an toàn 
                final_knowledge.pop(-1)#loại bỏ câu đó
        self.knowledge = final_knowledge
