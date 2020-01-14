from field2 import Field2
import copy

def rotate_clockwise(shape):
    return [ [ shape[y][x]
            for y in range(len(shape)) ]
        for x in range(len(shape[0]) - 1, -1, -1) ]


class Ai2:

    @staticmethod
    def best(field, workingPieces, workingPieceIndex, weights, level):
        bestRotation = None
        bestOffset = None
        bestScore = None
        workingPieceIndex = copy.deepcopy(workingPieceIndex)
        workingPiece = workingPieces[workingPieceIndex]
        shapes_rotation = { 4 : 4, 8 : 2, 12 : 2, 16 : 4, 20 : 4, 24 : 2, 28 : 1 }
        flat_piece = [val for sublist in workingPiece for val in sublist]
        hashedPiece = sum(flat_piece)

        for rotation in range(0, shapes_rotation[hashedPiece]):
            for offset in range(0, field.width):
                result = field.projectPieceDown(workingPiece, offset, level)
                if not result is None:
                    score = None
                    if workingPieceIndex == len(workingPieces)-1 :
                        heuristics = field.heuristics()
                        score = sum([a*b for a,b in zip(heuristics, weights)])
                    else:
                        _, _, score = Ai2.best(field, workingPieces, workingPieceIndex + 1, weights, 2)

                    if bestScore is None:
                        bestScore = score
                        bestOffset = offset
                        bestRotation = rotation

                    elif score > bestScore:
                        bestScore = score
                        bestOffset = offset
                        bestRotation = rotation
                field.undo(level)
            workingPiece = rotate_clockwise(workingPiece)

        return bestOffset, bestRotation, bestScore

    @staticmethod
    def choose(initialField, piece, next_piece, offsetX, weights, parent):
        field = Field2(len(initialField[0]), len(initialField))
        field.updateField(copy.deepcopy(initialField))

        offset, rotation, _ = Ai2.best(field, [piece, next_piece], 0, weights, 1)
        moves = []

        offset = offset - offsetX
        for _ in range(0, rotation):
            moves.append("w")
        for _ in range(0, abs(offset)):
            if offset > 0:
                moves.append("d")
            else:
                moves.append("a")
        #moves.append('RETURN')
        parent.executes_move(moves)
        #return moves
