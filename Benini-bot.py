class Benini(object):
    def __init__(self):
        self.name = "Benini"
        self.total_value = None
        self.history = []
        self.last_painting_value = None

    def get_bid_for_value_game(
        self,
        current_round,
        bots,
        artists_and_values,
        round_limit,
        starting_budget,
        painting_order,
        my_bot_details,
        current_painting,
        winner_ids,
        amounts_paid,
    ):
        current_painting_value = artists_and_values[current_painting]
        my_budget = my_bot_details["budget"]

        # update the current value of all the paintings
        if current_round == 0:
            self.total_value = sum(artists_and_values[i] for i in painting_order)
        else:
            self.total_value -= self.last_painting_value

        # play to win a lower number of painting than the total
        adaptive_total = self.total_value * np.random.uniform(0.4, 0.6)
        # when the total values of the remaining paintings goes down the mulitplier increase
        adaptive_multiplier = my_budget / adaptive_total

        # Track the history of bids
        if current_round > 0:
            self.history.append(
                [
                    winner_ids[current_round - 1],
                    amounts_paid[current_round - 1],
                    painting_order[current_round - 1],
                ]
            )

        # calculate average bid on the last 5 turns
        estimated_competitors_bid = self.estimate_competitors_bid(
            current_painting_value
        )

        # adjust bid to the values of the current painting
        bid = self.bid_adjuster(
            current_painting_value,
            adaptive_multiplier,
            estimated_competitors_bid,
        )

        self.last_painting_value = current_painting_value

        return min(bid, my_budget)

    def estimate_competitors_bid(self, current_painting_value):
        # if no history available bid the current painting value with some randomization
        if len(self.history) < 5:
            return current_painting_value
        else:
            recent_amounts_paid = [amount for _, amount, _ in self.history[-5:]]
            average_recent_amount_paid = sum(recent_amounts_paid) / len(
                recent_amounts_paid
            )
            # Normalize based on the median value of a painting
            estimated_amount = average_recent_amount_paid * (current_painting_value / 6)
            return estimated_amount

    def bid_adjuster(
        self,
        current_painting_value,
        adaptive_multiplier,
        estimated_competitors_bid,
    ):
        # high value paintings (Rembrant and Van gogh)
        if current_painting_value > 5:
            bid = max(
                # takes into consideration the current budget and the current painting's value
                adaptive_multiplier * current_painting_value,
                # increase the chances of winning high value paintings based on the average bid + a margin
                estimated_competitors_bid + (0.75 * current_painting_value),
            )
        # low value paintings (Picasso and Da Vinci)
        else:
            bid = min(
                # takes into consideration the current budget and the current painting's value
                adaptive_multiplier * current_painting_value,
                # conservative on low values paintings
                estimated_competitors_bid,
            )
        print(f"mine: {bid}")
        return bid
