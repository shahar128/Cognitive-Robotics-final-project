(define (domain pddl-domain)
 (:requirements :strips :typing :numeric-fluents)
 (:types item bin robot)
 (:predicates (inbin ?item - item ?bin - bin) (holding ?robot - robot ?item - item) (destination ?item - item ?bin - bin) (robot_at_bin ?robot - robot ?bin - bin) (robot_at_item ?robot - robot ?item - item) (robot_empty ?robot - robot))
 (:functions (timeremaining) (reward ?item - item ?bin - bin) (reward_robot) (duration_ ?item - item ?bin - bin))
 (:action move_to_item
  :parameters ( ?r - robot ?i - item ?b - bin)
  :precondition (and (robot_at_bin ?r ?b))
  :effect (and (not (robot_at_bin ?r ?b)) (robot_at_item ?r ?i) (assign (timeremaining) (- (timeremaining) (duration_ ?i ?b)))))
 (:action move_to_bin
  :parameters ( ?r - robot ?i - item ?b - bin)
  :precondition (and (robot_at_item ?r ?i))
  :effect (and (robot_at_bin ?r ?b) (not (robot_at_item ?r ?i)) (assign (timeremaining) (- (timeremaining) (duration_ ?i ?b)))))
 (:action pick_up
  :parameters ( ?r - robot ?i - item)
  :precondition (and (robot_at_item ?r ?i) (robot_empty ?r))
  :effect (and (holding ?r ?i) (not (robot_empty ?r)) (assign (timeremaining) (- (timeremaining) 7))))
 (:action place_in_bin
  :parameters ( ?r - robot ?i - item ?b - bin)
  :precondition (and (holding ?r ?i) (robot_at_bin ?r ?b) (destination ?i ?b))
  :effect (and (inbin ?i ?b) (not (holding ?r ?i)) (assign (reward_robot) (+ (reward ?i ?b) (reward_robot))) (assign (timeremaining) (- (timeremaining) 1))))
)
