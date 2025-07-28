import re
import collections
import sys
from typing import List, Tuple, Dict


class ShogiKifuParser:
    """A class to parse Shogi kifu files and convert them to SFEN format."""
    
    def __init__(self):
        # Japanese numeral conversions
        self.trans1 = ['１', '２', '３', '４', '５', '６', '７', '８', '９']
        self.trans2 = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
        
        # Piece mappings
        self.koma_moji = ['飛', '角', '金', '銀', '桂', '香', '歩']
        self.koma_kigo = ['r', 'b', 'g', 's', 'n', 'l', 'p']
        self.koma_kigo2 = [x.swapcase() for x in self.koma_kigo] + self.koma_kigo
        
        # Initial board position in SFEN format
        self.initial_position = 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL'
    
    def make_sfen(self, row_string: str) -> str:
        """Convert consecutive zeros to numbers in SFEN format."""
        for i in range(9, 0, -1):
            row_string = row_string.replace('0' * i, str(i))
        return row_string
    
    def normalize_kifu_text(self, kifu: str) -> str:
        """Normalize Japanese numerals and remove full-width spaces."""
        # Convert Japanese numerals to Arabic numerals
        for i in range(9):
            kifu = kifu.replace(self.trans1[i], str(i + 1))
            kifu = kifu.replace(self.trans2[i], str(i + 1))
        
        # Remove full-width spaces
        kifu = kifu.replace('\u3000', '')
        return kifu
    
    def extract_moves(self, kifu: str) -> List[str]:
        """Extract move sequences from kifu text."""
        moves = [match.groups()[0] 
                for match in re.finditer(r'^\s*[0-9]+\s+(\S+).*$', 
                                       kifu, 
                                       flags=re.MULTILINE)]
        
        # Replace '同' (same position) references
        for i in range(1, len(moves)):
            if '同' in moves[i]:
                moves[i] = moves[i].replace('同', moves[i-1][:2])
        
        # Remove resignation marker
        if '投了' in moves:
            moves.remove('投了')
        
        return moves
    
    def parse_piece_move(self, move_notation: str) -> Tuple[Tuple[int, int], Tuple[int, int], str, bool]:
        """Parse a piece movement notation."""
        match = re.match(r'^(\d{2})(\D+)\((\d{2}).*$', move_notation)
        if not match:
            raise ValueError(f"Invalid move notation: {move_notation}")
        
        destination, piece_info, origin = match.groups()
        
        # Convert coordinates (1-indexed to 0-indexed, flip x-axis)
        after_x = 9 - int(destination[0])
        after_y = int(destination[1]) - 1
        before_x = 9 - int(origin[0])
        before_y = int(origin[1]) - 1
        
        # Check for promotion
        is_promotion = piece_info.endswith('成')
        
        return (before_x, before_y), (after_x, after_y), piece_info, is_promotion
    
    def parse_piece_drop(self, move_notation: str) -> Tuple[Tuple[int, int], str]:
        """Parse a piece drop notation."""
        after_x = 9 - int(move_notation[0])
        after_y = int(move_notation[1]) - 1
        piece_char = move_notation[2]
        
        if piece_char not in self.koma_moji:
            raise ValueError(f"Invalid piece character: {piece_char}")
        
        piece_symbol = self.koma_kigo[self.koma_moji.index(piece_char)]
        return (after_x, after_y), piece_symbol
    
    def format_mochigoma_sfen(self, mochigoma: List[str]) -> str:
        """Format captured pieces (mochigoma) in SFEN notation."""
        if not mochigoma:
            return '-'
        
        mochigoma_dict = collections.Counter(''.join(mochigoma))
        sfen_mochigoma = ''
        
        for piece in self.koma_kigo2:
            count = mochigoma_dict.get(piece, 0)
            if count == 1:
                sfen_mochigoma += piece
            elif count > 1:
                sfen_mochigoma += str(count) + piece
        
        return sfen_mochigoma if sfen_mochigoma else '-'
    
    def process_moves(self, moves: List[str]) -> List[str]:
        """Process all moves and generate SFEN positions."""
        sfen_list = []
        mochigoma = []
        
        # Initialize board
        kyokumen = self.initial_position
        sfen_list.append(f"{kyokumen} b - 1")
        
        # Convert to matrix representation
        for i in range(1, 10):
            kyokumen = kyokumen.replace(str(i), '0' * i)
        kyokumen = [list(row) for row in kyokumen.split('/')]
        
        # Process each move
        for move_index, move in enumerate(moves):
            try:
                if not move.endswith('打'):  # Regular piece move
                    self._process_piece_move(move, kyokumen, mochigoma, move_index)
                else:  # Piece drop
                    self._process_piece_drop(move, kyokumen, mochigoma, move_index)
                
                # Generate SFEN for current position
                sfen_position = self._generate_sfen_position(kyokumen, mochigoma, move_index)
                sfen_list.append(sfen_position)
                
            except (ValueError, IndexError) as e:
                print(f"Error processing move {move_index + 1}: {move} - {e}", file=sys.stderr)
                continue
        
        return sfen_list
    
    def _process_piece_move(self, move: str, kyokumen: List[List[str]], 
                          mochigoma: List[str], move_index: int) -> None:
        """Process a regular piece movement."""
        (before_x, before_y), (after_x, after_y), piece_info, is_promotion = self.parse_piece_move(move)
        
        # Get the piece being moved
        active_piece = kyokumen[before_y][before_x]
        if active_piece == '0':
            raise ValueError(f"No piece at origin position ({before_x}, {before_y})")
        
        # Clear origin position
        kyokumen[before_y][before_x] = '0'
        
        # Handle promotion
        if is_promotion:
            active_piece = '+' + active_piece
        
        # Capture piece if present at destination
        captured_piece = kyokumen[after_y][after_x]
        if captured_piece != '0':
            # Remove promotion marker and swap case for captured piece
            captured_base = captured_piece.replace('+', '')
            mochigoma.append(captured_base[-1].swapcase())
        
        # Place piece at destination
        kyokumen[after_y][after_x] = active_piece
    
    def _process_piece_drop(self, move: str, kyokumen: List[List[str]], 
                          mochigoma: List[str], move_index: int) -> None:
        """Process a piece drop move."""
        (after_x, after_y), piece_symbol = self.parse_piece_drop(move)
        
        # Determine piece case based on player turn
        if move_index % 2 == 0:  # Sente (first player)
            active_piece = piece_symbol.upper()
        else:  # Gote (second player)
            active_piece = piece_symbol.lower()
        
        # Place piece on board
        kyokumen[after_y][after_x] = active_piece
        
        # Remove piece from captured pieces
        if active_piece not in mochigoma:
            raise ValueError(f"Piece {active_piece} not available for drop")
        mochigoma.remove(active_piece)
    
    def _generate_sfen_position(self, kyokumen: List[List[str]], 
                              mochigoma: List[str], move_index: int) -> str:
        """Generate SFEN notation for current position."""
        # Convert board to SFEN format
        board_sfen = '/'.join([self.make_sfen(''.join(row)) for row in kyokumen])
        
        # Determine active player
        active_player = 'w' if move_index % 2 == 0 else 'b'
        
        # Format captured pieces
        mochigoma_sfen = self.format_mochigoma_sfen(mochigoma)
        
        # Move number
        move_number = str(move_index + 2)
        
        return f"{board_sfen} {active_player} {mochigoma_sfen} {move_number}"
    
    def convert_kifu_to_sfen(self, input_file: str, output_file: str) -> None:
        """Main method to convert kifu file to SFEN format."""
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                kifu = f.read()
            
            # Process kifu
            normalized_kifu = self.normalize_kifu_text(kifu)
            moves = self.extract_moves(normalized_kifu)
            sfen_positions = self.process_moves(moves)
            
            # Write output file
            with open(output_file, "w", encoding='utf-8') as f:
                f.write('\n'.join(sfen_positions))
            
            print(f"Successfully converted {len(moves)} moves to SFEN format")
            print(f"Output written to: {output_file}")
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing kifu: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python move.py <input_file> <output_file>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    parser = ShogiKifuParser()
    parser.convert_kifu_to_sfen(input_file, output_file)


if __name__ == "__main__":
    main()
