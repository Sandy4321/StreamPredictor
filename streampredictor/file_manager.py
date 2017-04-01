from streampredictor.pop import Pop
from streampredictor import pop_manager
from streampredictor.category import Category


class FileManager():
    """
    Saves and loads the pop manager in different format.
    """

    def __init__(self, pm):
        """
        :type pm: pop_manager.PopManager
        """
        self.pop_manager = pm  # type: pop_manager.PopManager

    def save(self, predictor_filename, category_filename):
        self.save_predictors(predictor_filename)
        self.save_category(category_filename)

    def save_predictors(self, filename):
        header = '\t'.join(['pattern', 'strength', 'component1', 'component2', 'parents']) + '\n'
        save_string = header
        for key, pop in sorted(iter(self.pop_manager.pattern_collection.items()),
                               key=lambda ng: ng[1].strength,
                               reverse=True):
            save_string += key + '\t' + str(pop.strength) + '\t'
            if pop.first_component:
                save_string += pop.first_component.unrolled_pattern
            save_string += '\t'
            if pop.second_component:
                save_string += pop.second_component.unrolled_pattern
            save_string += '\t'
            for parent_i in pop.first_child_parents:
                save_string += parent_i.unrolled_pattern
                save_string += '\t'
            save_string += '\n'
        with open(filename, mode='w') as file:
            file.write(save_string)
        print('Saved file ' + filename + ' with pattern count ' + str(len((self.pop_manager.pattern_collection))))

    def save_category(self, filename):
        header = '\t'.join(['category_name', 'strength', 'members of category']) + '\n'
        save_string = header
        for name, category in sorted(iter(self.pop_manager.category_collection.items()),
                                     key=lambda ng: ng[1].strength,
                                     reverse=True):
            save_string += name + '\t' + str(category.strength) + '\t'
            for member in category.members:
                save_string += member.unrolled_pattern
                save_string += '\t'
            save_string += '\n'
        with open(filename, mode='w') as file:
            file.write(save_string)
        print('Saved file ' + filename + ' with pattern count ' + str(len((self.pop_manager.pattern_collection))))

    def load(self, predictors_filename, categories_filename):
        self.load_predictor(predictors_filename)
        self.load_categories(categories_filename)

    def load_predictor(self, filename):
        with open(filename, mode='r') as file:
            all_lines = file.readlines()
            data_lines = all_lines[1:]  # skip header
            self.get_keys_and_strength(data_lines)
            self.connect_pops(data_lines)
        print('Loaded file ' + filename
              + ' with number of patterns = ' + str(len(self.pop_manager.pattern_collection)))

    def load_categories(self, filename):
        with open(filename, mode='r') as file:
            all_lines = file.readlines()
            data_lines = all_lines[1:]  # skip header
            for line in data_lines:
                elements = line.strip('\n').split('\t')
                key = elements[0]
                strength = int(elements[1])
                members = [self.pop_manager.pattern_collection[i] for i in elements[2:] if i is not '']
                self.pop_manager.category_collection[key] = Category(key, strength, members)
        print('Loaded category file ' + filename
              + ' with number of categories = ' + str(len(self.pop_manager.category_collection)))

    def connect_pops(self, data_lines):
        for lines in data_lines:
            elements = lines.strip('\n').split('\t')
            key = elements[0]
            current_pop = self.pop_manager.get(key)
            if elements[2] is not '' and elements[3] is not '':
                first_component = self.pop_manager.get(elements[2])
                second_component = self.pop_manager.get(elements[3])
                current_pop.set_components(first_component, second_component)
            # elements 4 + are parents
            if elements[4] != '':
                for parent_i in elements[4:]:
                    if parent_i != '' and parent_i in self.pop_manager.pattern_collection:
                        parent_pop = self.pop_manager.get(parent_i)
                        current_pop.first_child_parents.append(parent_pop)

    def get_keys_and_strength(self, data_lines):
        for line in data_lines:
            elements = line.split('\t')
            key = elements[0]
            self.pop_manager.pattern_collection[key] = Pop(key)
            self.pop_manager.pattern_collection[key].strength = int(elements[1])
