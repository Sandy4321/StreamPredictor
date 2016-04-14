import ProtobufManager
from Pop import Pop


class FileManager():
    """
    Saves and loads the pop manager in different format.
    """

    def __init__(self, pm):
        self.pop_manager = pm

    def save_tsv(self, filename):
        save_string = 'pattern, strength, component1, component2, parents\n'
        for key, pop in sorted(self.pop_manager.patterns_collection.iteritems(), key=lambda ng: ng[1].strength):
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
        print 'Saved file ' + filename

    def save_pb(self, filename):
        buf = ProtobufManager.ProtobufManager.PopManager_to_ProtobufPopManager(self.pop_manager)
        ProtobufManager.ProtobufManager.save_protobuf(buf, filename)

    def save_pb_plain(self, filename):
        buf = ProtobufManager.ProtobufManager.PopManager_to_ProtobufPopManager(self)
        ProtobufManager.ProtobufManager.save_protobuf_plain(buf, filename)

    def load_tsv(self, filename):
        partial_loading = False# doesn't work for now, some patterns will have first
        limit = 0              #parent child which is not loaded
        with open(filename, mode='r') as file:
            all_lines = file.readlines()
            total_lines = len(all_lines)
            if partial_loading:
                start_line = max(0, total_lines - limit)
                lines_to_read = all_lines[1 + start_line:]
            else:
                lines_to_read = all_lines[1:]
            for lines in lines_to_read:
                elements = lines.split('\t')
                key = elements[0]
                self.pop_manager.patterns_collection[key] = Pop(key)
                self.pop_manager.patterns_collection[key].strength = int(elements[1])
            for lines in all_lines[1:]:
                elements = lines.strip('\n').split('\t')
                key = elements[0]
                if elements[2] is not '' and elements[3] is not '':
                    self.pop_manager.set_components_from_string(self.pop_manager.patterns_collection[key], elements[2], elements[3])
                if elements[4] != '':
                    for parent_i in elements[4:]:
                        if parent_i != '' and parent_i in self.pop_manager.patterns_collection:
                            self.pop_manager.patterns_collection[key].first_child_parents.append(self.pop_manager.patterns_collection[parent_i])
        print 'Loaded file ' + filename + ' with number of patterns = ' + str(len(self.pop_manager.patterns_collection))

    def load_pb(self, filename):
        pop_manager = ProtobufManager.ProtobufManager.load_PopManager(filename)
        self.pop_manager.patterns_collection = pop_manager.patterns_collection

    def load_pb_plain(self, filename):
        buffy = ProtobufManager.ProtobufManager.load_protobuf_plain(filename)
        pm = ProtobufManager.ProtobufManager.protobuf_to_pop_manager(buffy)
        self.pop_manager.patterns_collection = pm.patterns_collection
