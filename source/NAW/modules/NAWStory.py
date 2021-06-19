# NAW event class by SemD
import random

from source.NAW.modules.NAWFilesControl import NAWFilesControl as Files

Files.check_version()


class NAWStory:
    first_part = '0|00|0|000|000|00|00|00|0|0|0|0000|0|00|0|000'
    second_part = '0|00|00|00|00|0|0|00|00|0|0|0|0|0|0|00|0|0|0|0|0|0|0|00'
    third_part = '00|0|0|00|00|0|0|0|00|00|0|0|0|0|0|0|0|0|0|00|0|0|0|0|0|0|0|0|0|0'
    all_part = [first_part, second_part, third_part]

    @classmethod
    def get_all_path(cls):
        all_path = ''
        for part in cls.all_part:
            all_path += part + '|'
        return all_path

    def __init__(self, step, path, position):
        self._current_step = step
        self._current_position = position
        self._path = path
        self._selected_variant = None
        self._next_step = None
        self._next_event = None
        self._next_position = None
        self._current_event = self.get_current_event()

    def get_current_event(self):
        current_step_events = Files.get_node(str(self._current_step), 'story')
        return current_step_events[self._current_position]

    def user_reaction(self, variant=None):
        if variant:
            if self._current_event['variants']:
                self._selected_variant = variant
                if self._selected_variant not in self._current_event['variants']:
                    return {}
            else:
                try:
                    if not self._current_event['dialog']:
                        return {}
                    else:
                        dialog_text = Files.get_node(str(self._current_step))[0]['text']

                        # add try catch block for @ValueError -> is not in list@

                        dialog_position = dialog_text.index(variant)
                        if dialog_position != len(dialog_text) - 1:
                            return {'step': self._current_step, 'text-position': dialog_position}
                except KeyError:
                    return {}
        self._next_step = self._current_event['depend step']
        if self._next_step == 0:
            return {'step': 0}
        self.set_new_step()
        try:
            if self._next_event['dialog']:
                cur_part_path = list(self._path[self._current_step])
                cur_part_path[self._current_position] = '1'
                self._path[self._current_step] = ''.join(cur_part_path)
                return {'step': self._next_step, 'text-position': 0, 'path': self._path,
                        'position': self._next_position}
        except KeyError:
            pass
        return self.set_new_path()

    def set_new_step(self):
        if self._selected_variant:
            self._next_position = self._current_event['variants'].index(self._selected_variant)
        else:
            try:
                if self._current_event['to position'] >= 0:
                    to_position = self._current_event['to position']
                    try:
                        if self._current_event['chance']:
                            has_chance = random.randint(1, 100)
                            if int(self._current_event['chance']) <= has_chance:
                                try:
                                    if self._current_event['else']:
                                        if self._current_event['else'] == '0.0':
                                            pass
                                            # game over
                                        else:
                                            to_position = self._current_event['else']
                                except KeyError:
                                    to_position = self._current_event['depend of']
                    except KeyError:
                        pass
                    if type(to_position) == float:
                        self._next_step = int(str(to_position).split('.')[0])
                        self._next_position = int(str(to_position).split('.')[1])
                    else:
                        self._next_position = to_position
            except KeyError:
                self._next_position = 0
        self._next_event = Files.get_node(str(self._next_step), 'story')[self._next_position]
        try:
            if self._next_event["if"]:
                if_event_arr = str(self._next_event["if"]).split('.')
                if self._path[int(if_event_arr[0])][int(if_event_arr[1])] != '1':
                    if type(self._next_event["else-if"]) == float:
                        else_event_arr = str(self._next_event["else-if"]).split('.')
                        self._next_step = int(else_event_arr[0])
                        self._next_position = int(else_event_arr[1])
                        self._next_event = Files.get_node(str(self._next_step), 'story')[self._next_position]
                    else:
                        self._next_position = self._next_event["else-if"]
                        self._next_event = Files.get_node(str(self._next_step), 'story')[self._next_position]
        except KeyError:
            pass

    def get_send_text(self):
        step_texts = Files.get_node(str(self._next_step))
        if self._path[self._next_step][self._next_position] != '1':
            return step_texts[self._next_position]['text']
        else:
            try:
                return step_texts[self._next_position]['marked']
            except KeyError:
                if self._next_event['variants']:
                    return '0'
                return step_texts[self._next_position]['text']

    def set_new_path(self):
        cur_part_path = list(self._path[self._current_step])
        cur_part_path[self._current_position] = '1'
        self._path[self._current_step] = ''.join(cur_part_path)
        return {'path': self._path, 'step': self._next_step, 'position': self._next_position,
                'variants': self._next_event['variants']}
