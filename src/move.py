'''
Module contains class Move, which is a standardized way of conveying character turn
information.
'''

from typing import Any, SupportsIndex


class Move:

    def __init__(self, source_square, destination_square, target_square, action_type=None, action_id=None, value=0) -> None:
        
        self.source_square      = source_square
        self.destination_square = destination_square
        self.target_square      = target_square
        self.action_type        = action_type
        self.action_id          = action_id
        self.value              = value

    def __repr__(self) -> str:
        return f"MOVE: Source: {self.source_square}, destination: {self.destination_square}, target:{self.target_square}, type: {self.action_type}, id: {self.action_id}, value: {self.value}"