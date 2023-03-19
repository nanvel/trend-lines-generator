#     def source_y(self, x: Union[int, datetime.datetime]) -> float:
#         if self.board.x_is_datetime:
#             x = Time.from_datetime(x)
#         x = int((int(x) - self.board.x_start) / self.board.x_step)
#         return self.board.y_start + self.board_y(x) * self.board.y_step
