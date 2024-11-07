class StateMachine:
    def __init__(self):
        self.current_state = None

    def update(self):

        if self.current_state is not None:
            new_state = self.current_state.check_transitions()
            if new_state is not None:
                self.change_state(new_state)


            self.current_state.execute()

    def change_state(self, new_state):

        if self.current_state is not None:
            self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

    def handle_event(self, event):
        if self.current_state is not None:
            new_state = self.current_state.check_transitions(event)
            if new_state is not None:
                self.change_state(new_state)

class State:
    def __init__(self):
        self.transitions = []

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass

    def add_transition(self, transition):
        self.transitions.append(transition)

    def check_transitions(self):
        for transition in self.transitions:
            if transition.is_triggered():
                return transition.get_target_state()
        return None
    
class Transition:
    def __init__(self, target_state, condition):
        self.target_state = target_state
        self.condition = condition    

    def is_triggered(self):
        return self.condition()

    def get_target_state(self):
        return self.target_state


