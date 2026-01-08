
from schnapsen.game import Bot, Move, PlayerPerspective
# other needed imports here. Most likely you need:
from schnapsen.game import Marriage
from schnapsen.deck import Card, Suit, Rank


class AssignmentBot(Bot):
    """Your suit order is [SPADES, HEARTS, CLUBS, DIAMONDS], from lower suit to higher suit."""


    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """Get the move for the Bot.
        The basic structure for your bot is already implemented and must not be modified.
        To implement your bot, only modify the condition and action methods below.
        """
        if self.condition1(perspective, leader_move):
            return self.action1(perspective, leader_move)
        elif self.condition2(perspective, leader_move):
            if self.condition3(perspective, leader_move):
                return self.action2(perspective, leader_move)
            else:
                return self.action3(perspective, leader_move)
        else:
            return self.action4(perspective, leader_move)

    def condition1(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """1. if the bot can play a royal marriage [1 point]"""
        
        if leader_move is not None:
            return False

        trump_suit = perspective.get_trump_suit()
        hand = perspective.get_hand().get_cards()
        
        king_check = False
        queen_check = False
        
        for card in hand:
            if card.suit == trump_suit:
                if card.rank == Rank.KING:
                    king_check = True
                if card.rank == Rank.QUEEN:
                    queen_check = True
            
        return king_check and queen_check

    def condition2(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """2. otherwise, if the 🂡 (ACE_SPADES) has not been won yet by either bot [1 point]"""
        
        for card in perspective.get_won_cards().get_cards():
            if card.suit == Suit.SPADES and card.rank == Rank.ACE:
                return False
        
        for card in perspective.get_opponent_won_cards().get_cards():
            if card.suit == Suit.SPADES and card.rank == Rank.ACE:
                return False
            
        return True

    def condition3(self, perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """                  a. if it is the second phase of the game and the opponent has more CLUBS than
                        DIAMONDS or equal the number in their hand [1.5 points]"""
        if perspective.get_talon_size() == 0:
            opponent_hand = perspective.get_known_cards_of_opponent_hand().get_cards()
            clubs_count = 0
            diamonds_count = 0
                    
            for card in opponent_hand:
                if card.suit == Suit.CLUBS:
                    clubs_count += 1
                elif card.suit == Suit.DIAMONDS:
                    diamonds_count += 1
                    
            return clubs_count >= diamonds_count

        return False
                    
    def action1(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """   then play the royal marriage  [1.5 point]"""
        marriage_king = None
        marriage_queen = None
        
        for card in perspective.get_hand().get_cards():
            if card.rank == Rank.KING and card.suit == perspective.get_trump_suit():
                marriage_king = card
                
            elif card.rank == Rank.QUEEN and card.suit == perspective.get_trump_suit():
                marriage_queen = card
                
        if marriage_king and marriage_queen:
            return Marriage(marriage_queen, marriage_king)
        
        return perspective.valid_moves()[0]

    def action2(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """                     then play the valid regular move where the card has the lowest suit according
                          to the suit order above. If multiple cards have the lowest suit,
                          prioritize according to lowest points. [1.5 points]"""
        
        suits_map = {Suit.SPADES: 1, Suit.HEARTS: 2, Suit.CLUBS: 3, Suit.DIAMONDS: 4}
        rank_map = {Rank.ACE: 11, Rank.TEN: 10, Rank.KING: 4, Rank.QUEEN: 3, Rank.JACK: 2}
        
        valid_moves = perspective.valid_moves()
        regular_moves = []
        
        for move in valid_moves:
            if move.is_regular_move():
                regular_moves.append(move)
        
        if not regular_moves:
            return perspective.valid_moves()[0]
        
        return_move = regular_moves[0]
        
        for move in regular_moves:
            current_priority = suits_map[move.card.suit]
            best_priority = suits_map[return_move.card.suit]
            
            if current_priority < best_priority:
                return_move = move
            
            elif current_priority == best_priority:
                current_points = rank_map[move.card.rank]
                best_points = rank_map[return_move.card.rank]
                
                if current_points < best_points:
                    return_move = move
        
        return return_move
                    
    def action3(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """                  b. otherwise among the cards in valid regular moves, take the cards with the most
                               frequently occurring rank. If there are multiple ranks with equal
                               most frequency, take the one with the highest points. Among those.
                               take the card with the highest suit, according to the order above. [2.0 points]"""
                               
        valid_moves = perspective.valid_moves()
        regular_moves = []
        
        suits_map = {Suit.SPADES: 1, Suit.HEARTS: 2, Suit.CLUBS: 3, Suit.DIAMONDS: 4}
        rank_map = {Rank.ACE: 11, Rank.TEN: 10, Rank.KING: 4, Rank.QUEEN: 3, Rank.JACK: 2}
        
        for move in valid_moves:
            if move.is_regular_move():
                regular_moves.append(move)
                
        if not regular_moves:
            return perspective.valid_moves()[0]
        
        rank_frequency = {}
        
        for move in regular_moves:
            if move.card.rank not in rank_frequency:
                rank_frequency[move.card.rank] = 1
                
            elif move.card.rank in rank_frequency:
                rank_frequency[move.card.rank] += 1
                
        return_move = regular_moves[0]
        
        for move in regular_moves:
            current_rank = move.card.rank
            best_rank = return_move.card.rank
            
            if rank_frequency[current_rank] > rank_frequency[best_rank]:
                return_move = move
            
            elif rank_frequency[current_rank] == rank_frequency[best_rank]:
                if rank_map[current_rank] > rank_map[best_rank]:
                    return_move = move
                
                elif rank_map[current_rank] == rank_map[best_rank]:
                    if suits_map[move.card.suit] > suits_map[return_move.card.suit]:
                        return_move = move
        
        return return_move
        
    def action4(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """3. otherwise take the cards in valid regular moves and order them by points (low to high); in this
             ordering, if two cards have the same points, sort these according to the suit order.
             Now, play the card in the middle of the sequence. If the number of cards is even, play
             the card right below the middle. [1.5 points]"""
             
        valid_moves = perspective.valid_moves()
        regular_moves = []
        
        suits_map = {Suit.SPADES: 1, Suit.HEARTS: 2, Suit.CLUBS: 3, Suit.DIAMONDS: 4}
        rank_map = {Rank.ACE: 11, Rank.TEN: 10, Rank.KING: 4, Rank.QUEEN: 3, Rank.JACK: 2}
        
        for move in valid_moves:
            if move.is_regular_move():
                regular_moves.append(move)
        
        if not regular_moves:
            return perspective.valid_moves()[0]
                            
        for i in range(len(regular_moves)):
            for j in range(0, len(regular_moves) - i - 1):
                current_move = regular_moves[j]
                next_move = regular_moves[j + 1]
                
                current_points = rank_map[current_move.card.rank]
                next_points = rank_map[next_move.card.rank]
                
                swap = False
                
                if current_points > next_points:
                    swap = True
                    
                elif current_points == next_points:
                    if suits_map[current_move.card.suit] > suits_map[next_move.card.suit]:
                        swap = True
                
                if swap:
                    temp_move = regular_moves[j]
                    regular_moves[j] = regular_moves[j + 1]
                    regular_moves[j + 1] = temp_move
            
        middle_index = (len(regular_moves) - 1) // 2
        return regular_moves[middle_index]